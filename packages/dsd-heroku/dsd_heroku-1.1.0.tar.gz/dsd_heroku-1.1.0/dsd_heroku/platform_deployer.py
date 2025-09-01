"""Manages all Heroku-specific aspects of the deployment process."""

import sys, os, re, json, subprocess
from pathlib import Path
from itertools import takewhile

from django.conf import settings
from django.core.management.utils import get_random_secret_key
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

import toml

# from ..utils import plugin_utils
# from ..utils.plugin_utils import dsd_config
# from ..utils.command_errors import DSDCommandError
from django_simple_deploy.management.commands.utils import plugin_utils
from django_simple_deploy.management.commands.utils.plugin_utils import dsd_config
from django_simple_deploy.management.commands.utils.command_errors import (
    DSDCommandError,
)

from . import deploy_messages as platform_msgs


class PlatformDeployer:
    """Perform the initial deployment to Heroku.

    If --automate-all is used, carry out an actual deployment.
    If not, do all configuration work so the user only has to commit changes, and run
    `git push heroku main`.
    """

    def __init__(self):
        """Establishes connection to existing simple_deploy command object."""
        self.templates_path = Path(__file__).parent / "templates"

    # --- Public methods ---

    def deploy(self, *args, **options):
        plugin_utils.write_output("\nConfiguring project for deployment to Heroku...")

        self._validate_platform()

        self._handle_poetry()
        self._prep_automate_all()
        self._ensure_db()
        self._add_requirements()
        self._set_env_vars()
        self._add_procfile()
        self._add_static_file_directory()
        self._modify_settings()

        self._conclude_automate_all()
        self._summarize_deployment()
        self._show_success_message()

    # --- Helper methods for deploy() ---

    def _validate_platform(self):
        """Make sure the local environment and project supports deployment to Heroku.

        Returns:
            None

        Raises:
            DSDCommandError: If we find any reason deployment won't work.
        """
        self._check_heroku_settings()
        self._check_cli_installed()
        self._check_cli_authenticated()
        self._check_heroku_project_available()

    def _handle_poetry(self):
        """Respond appropriately if the local project uses Poetry.

        If the project uses Poetry, generate a requirements.txt file, and override the
        initial value of dsd_config.pkg_manager.

        Heroku doesn't work directly with Poetry, so we need to generate a
        requirements.txt file for the user, which we can then add requirements to. We
        should inform the user about this, as they may be used to just working with
        Poetry's requirements specification files.

        This should probably be addressed in the success message as well, and in the
        summary file. They will need to update the requirements.txt file whenever they
        install additional packages.

        Note that there may be a better way to approach this, such as adding
        requirements to Poetry files before generating the requirements.txt file for
        Heroku. It's not good to have a requirements.txt file that doesn't match what
        Poetry sees in the project.

        See Issue 31:
        https://github.com/ehmatthes/django-simple-deploy/issues/31#issuecomment-973147728

        Returns:
            None
        """
        # Making this check here keeps deploy() cleaner.
        if dsd_config.pkg_manager != "poetry":
            return

        msg = "  Generating a requirements.txt file, because Heroku does not support Poetry directly..."
        plugin_utils.write_output(msg)

        # Poetry 2.0 removed built-in support for `export`. Exporting to
        # requirements.txt now requires the poetry-plugin-export plugin.
        self._check_poetry_export_plugin()

        cmd = "poetry export -f requirements.txt --output requirements.txt --without-hashes"
        output = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output)

        msg = "    Wrote requirements.txt file."
        plugin_utils.write_output(msg)

        # From this point forward, treat this user the same as anyone who's using a bare
        # requirements.txt file.
        dsd_config.pkg_manager = "req_txt"
        dsd_config.req_txt_path = dsd_config.git_path / "requirements.txt"
        plugin_utils.log_info("    Package manager set to req_txt.")
        plugin_utils.log_info(f"    req_txt path: {dsd_config.req_txt_path}")

        # Add simple_deploy, because it wasn't done earlier for poetry.
        # This may be a bug in how poetry is handled by core.
        plugin_utils.add_package("django-simple-deploy")

    def _prep_automate_all(self):
        """Do intial work for automating entire process.
        - Create a heroku app to deploy to.
        - Create a Heroku Postgres database.

        Sets:
            str: self.heroku_app_name

        Returns:
            None
        """
        if not dsd_config.automate_all:
            return

        # Create heroku app.
        plugin_utils.write_output("  Running `heroku create`...")
        cmd = "heroku create --json"
        output_obj = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output_obj)

        # Get name of app.
        output_json = json.loads(output_obj.stdout.decode())
        self.heroku_app_name = output_json["name"]

        self._create_postgres_db()

    def _ensure_db(self):
        """Ensure a db is available, or create one.

        Returns:
            None
        """
        # DB not needed for unit testing.
        if dsd_config.unit_testing:
            return
        # DB already created for automate-all.
        if dsd_config.automate_all:
            return

        # Look for a Postgres database.
        addons_list = self.apps_list["addons"]
        db_exists = False
        for addon_dict in addons_list:
            # Look for a plan name indicating a postgres db.
            try:
                plan_name = addon_dict["plan"]["name"]
            except KeyError:
                pass
            else:
                if "heroku-postgresql" in plan_name:
                    db_exists = True
                    break

        if db_exists:
            msg = f"  Found a {plan_name} database."
            plugin_utils.write_output(msg)
            return

        msg = f"  Could not find an existing database. Creating one now..."
        plugin_utils.write_output(msg)
        self._create_postgres_db()

    def _add_requirements(self):
        """Add Heroku-specific requirements."""
        # psycopg2 2.9 causes "database connection isn't set to UTC" issue.
        #   See: https://github.com/ehmatthes/heroku-buildpack-python/issues/31
        packages = ["gunicorn", "psycopg2", "dj-database-url", "whitenoise"]
        plugin_utils.add_packages(packages)

    def _set_env_vars(self):
        """Set Heroku-specific environment variables."""
        if dsd_config.unit_testing:
            return

        self._set_heroku_env_var()
        self._set_debug_env_var()
        self._set_secret_key_env_var()
        self._set_settings_module_env_var()

    def _add_procfile(self):
        """Add Procfile to project."""
        # Generate Procfile contents.
        wsgi_path = f"{dsd_config.local_project_name}.wsgi"
        if dsd_config.nested_project:
            wsgi_path = f"{dsd_config.local_project_name}.{wsgi_path}"
        proc_command = f"web: gunicorn {wsgi_path} --log-file -"

        # Write Procfile.
        path = dsd_config.project_root / "Procfile"
        plugin_utils.add_file(path, proc_command)

    def _add_static_file_directory(self):
        """Create a folder for static files, if it doesn't already exist."""
        # Make sure directory exists.
        path_static = dsd_config.project_root / "static"
        plugin_utils.add_dir(path_static)

        # If static/ is not empty, we don't need to do anything.
        if any(path_static.iterdir()):
            plugin_utils.write_output("    Found non-empty static files directory.")
            return

        # static/ is empty; add a placeholder file to the directory.
        path_placeholder = path_static / "placeholder.txt"
        msg = "This is a placeholder file to make sure this folder is pushed to Heroku."
        plugin_utils.add_file(path_placeholder, msg)

    def _modify_settings(self):
        """Add Heroku-specific settings.

        DEV: The ALLOWED_HOSTS setting should be customized.
        """
        if dsd_config.settings_path.parts[-2:] == ("settings", "production.py"):
            template_path = self.templates_path / "settings_wagtail.py"
        else:
            template_path = self.templates_path / "settings.py"

        plugin_utils.modify_settings_file(template_path)

    def _conclude_automate_all(self):
        """Finish automating the push to Heroku."""
        if not dsd_config.automate_all:
            return

        plugin_utils.commit_changes()

        plugin_utils.write_output("  Pushing to heroku...")

        # Get the current branch name.
        cmd = "git branch --show-current"
        output_obj = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output_obj)
        self.current_branch = output_obj.stdout.decode().strip()

        # Push current local branch to Heroku main branch.
        # DEV: Note that the output of `git push heroku` goes to stderr, not stdout.
        plugin_utils.write_output(f"    Pushing branch {self.current_branch}...")
        if self.current_branch in ("main", "master"):
            cmd = f"git push heroku {self.current_branch}"
        else:
            cmd = f"git push heroku {self.current_branch}:main"
        plugin_utils.run_slow_command(cmd)

        # Run initial set of migrations.
        plugin_utils.write_output("  Migrating deployed app...")
        if dsd_config.nested_project:
            cmd = f"heroku run python {dsd_config.local_project_name}/manage.py migrate"
        else:
            cmd = "heroku run python manage.py migrate"
        output = plugin_utils.run_quick_command(cmd)

        plugin_utils.write_output(output)

        # Open Heroku app, so it simply appears in user's browser.
        plugin_utils.write_output("  Opening deployed app in a new browser tab...")
        cmd = "heroku open"
        output = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output)

    def _summarize_deployment(self):
        """Manage all tasks related to generating and showing the friendly
        summary of the deployment.

        This does not take the place of the platform's official documentation.
          Instead, it gives the user a friendly entry into the platform's
          official documentation. It also gives them a brief summary of some
          followup steps they can take, for example making a second push, or
          changing the URL of the deployed app.
        """
        self._generate_summary()

    def _show_success_message(self):
        """After a successful run, show a message about what to do next."""

        # DEV:
        # - Say something about DEBUG setting.
        #   - Should also consider setting DEBUG = False in the Heroku-specific
        #     settings.
        # - Mention that this script should not need to be run again, unless
        #   creating a new deployment.
        #   - Describe ongoing approach of commit, push, migrate. Lots to consider
        #     when doing this on production app with users, make sure you learn.

        if dsd_config.automate_all:
            # Show how to make future deployments.
            msg = platform_msgs.success_msg_automate_all(
                self.heroku_app_name, self.current_branch
            )
        else:
            # Show steps to finish the deployment process.
            msg = platform_msgs.success_msg(
                dsd_config.pkg_manager, self.heroku_app_name
            )

        plugin_utils.write_output(msg)

    # --- Utility methods ---

    def _check_heroku_settings(self):
        """Check to see if a Heroku settings block already exists."""
        start_line = "# Heroku settings."
        plugin_utils.check_settings(
            "Heroku",
            start_line,
            platform_msgs.heroku_settings_found,
            platform_msgs.cant_overwrite_settings,
        )

    def _check_cli_installed(self):
        """Verify the Heroku CLI is installed on the user's system.

        Returns:
            None

        Raises:
            DSDCommandError: If CLI not installed.
        """
        if dsd_config.unit_testing:
            return

        cmd = "heroku --version"
        try:
            output_obj = plugin_utils.run_quick_command(cmd)
        except FileNotFoundError:
            # This generates a FileNotFoundError on Linux (Ubuntu) if CLI not installed.
            raise DSDCommandError(platform_msgs.cli_not_installed)

        plugin_utils.log_info(output_obj)

        # The returncode for a successful command is 0, so anything truthy means the
        # command errored out.
        if output_obj.returncode:
            raise DSDCommandError(platform_msgs.cli_not_installed)

    def _check_cli_authenticated(self):
        """Verify the user has authenticated with the CLI.

        Returns:
            None

        Raises:
            DSDCommandError: If the user has not been authenticated.
        """
        if dsd_config.unit_testing:
            return

        cmd = "heroku auth:whoami"
        output_obj = plugin_utils.run_quick_command(cmd)
        plugin_utils.log_info(output_obj)

        output_str = output_obj.stderr.decode()
        # I believe I've seen both of these messages when not logged in.
        if ("Error: Invalid credentials provided" in output_str) or (
            "Error: not logged in" in output_str
        ):
            raise DSDCommandError(platform_msgs.cli_not_authenticated)

    def _check_heroku_project_available(self):
        """Verify that a Heroku project is available to push to.

        Assume the user has already run `heroku create.`

        Returns:
            None

        Raises:
            DSDCommandError: If there's no app to push to.

        Sets:
            dict: self.apps_list
            str: self.heroku_app_name
        """
        if dsd_config.unit_testing:
            self.heroku_app_name = "sample-name-11894"
            return

        # automate-all does the work we're checking for here.
        if dsd_config.automate_all:
            return

        plugin_utils.write_output("  Looking for Heroku app to push to...")
        cmd = "heroku apps:info --json"
        output_obj = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output_obj)

        output_str = output_obj.stdout.decode()

        # If output_str is emtpy, there is no heroku app.
        if not output_str:
            raise DSDCommandError(platform_msgs.no_heroku_app_detected)

        # Parse output for app_name.
        self.apps_list = json.loads(output_str)
        app_dict = self.apps_list["app"]
        self.heroku_app_name = app_dict["name"]
        plugin_utils.write_output(f"    Found Heroku app: {self.heroku_app_name}")

    def _check_poetry_export_plugin(self):
        """Make sure poetry-export-plugin is available."""
        cmd = "poetry self show plugins"
        output = plugin_utils.run_quick_command(cmd)
        if "poetry-plugin-export" not in output.stdout.decode():
            self._install_poetry_export_plugin()

    def _install_poetry_export_plugin(self):
        """Install poetry-export-plugin, so we can export requirements."""
        cmd = "poetry self add poetry-plugin-export"

        msg = "In order to continue, the plugin poetry-plugin-export needs to be installed."
        msg += (
            "\nThis is used to export pyproject.toml requirements to requirements.txt,"
        )
        msg += "\nwhich Heroku can parse."
        msg += "\nThe following command will be run:"
        msg += f"\n  $ {cmd}"
        msg += "\nIs it okay to install the poetry-plugin-export plugin?"
        plugin_utils.get_confirmation(msg)

        output = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output)

    def _create_postgres_db(self):
        """Create a Heroku Postgres database.

        Returns:
            None
        """
        plugin_utils.write_output("  Creating Postgres database...")
        plugin_utils.write_output("  (This may take several minutes.)")
        cmd = "heroku addons:create heroku-postgresql:essential-0 --wait"
        output = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output)

    def _set_heroku_env_var(self):
        """Set a config var to indicate when we're in the Heroku environment.
        This is mostly used to modify settings for the deployed project.
        """
        # Don't need this env var for Wagtail projects.
        if dsd_config.settings_path.parts[-2:] == ("settings", "production.py"):
            return
            
        plugin_utils.write_output("  Setting Heroku environment variable...")
        cmd = "heroku config:set ON_HEROKU=1"
        output = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output)
        plugin_utils.write_output("    Set ON_HEROKU=1.")
        plugin_utils.write_output(
            "    This is used to define Heroku-specific settings."
        )

    def _set_debug_env_var(self):
        """Use an env var to manage DEBUG setting, and set to False."""

        # Config variables are strings, which always causes confusion for people
        #   when setting boolean env vars. A good habit is to use something other than
        #   True or False, so it's clear we're not trying to use Python's default
        #   boolean values.
        # Here we use 'TRUE' and 'FALSE'. Then a simple test:
        #    os.environ.get('DEBUG') == 'TRUE'
        # returns the bool value True for 'TRUE', and False for 'FALSE'.
        # Taken from: https://stackoverflow.com/a/56828137/748891
        plugin_utils.write_output("  Setting DEBUG env var...")
        cmd = "heroku config:set DEBUG=FALSE"
        output = plugin_utils.run_quick_command(cmd)
        plugin_utils.write_output(output)
        plugin_utils.write_output("    Set DEBUG config variable to FALSE.")

    def _set_secret_key_env_var(self):
        """Use an env var to manage the secret key."""
        # Generate a new key.
        if dsd_config.on_windows:
            # Non-alphanumeric keys have been problematic on Windows.
            new_secret_key = get_random_string(
                length=50, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789"
            )
        else:
            new_secret_key = get_random_secret_key()

        # Set the new key as an env var on Heroku.
        plugin_utils.write_output("  Setting new secret key for Heroku...")
        cmd = f"heroku config:set SECRET_KEY={new_secret_key}"
        output = plugin_utils.run_quick_command(cmd, skip_logging=True)
        plugin_utils.write_output(output)
        plugin_utils.write_output("    Set SECRET_KEY config variable.")

    def _set_settings_module_env_var(self):
        """Set the DJANGO_SETTINGS_MODULE env var if needed."""
        # This is primarily for Wagtail projects, as signified by a settings/production.py file.
        if dsd_config.settings_path.parts[-2:] == ("settings", "production.py"):
            plugin_utils.write_output("  Setting DJANGO_SETTINGS_MODULE environment variable...")

            # Need form mysite.settings.production
            dotted_settings_path = ".".join(dsd_config.settings_path.parts[-3:]).removesuffix(".py")

            cmd = f"heroku config:set DJANGO_SETTINGS_MODULE={dotted_settings_path}"
            output = plugin_utils.run_quick_command(cmd)
            plugin_utils.write_output(output)
            plugin_utils.write_output("    Set SECRET_KEY config variable.")

    def _generate_summary(self):
        """Generate the friendly summary, which is html for now."""
        # Generate the summary file.
        # path = dsd_config.log_dir_path / "deployment_summary.html"

        # summary_str = "<h2>Understanding your deployment</h2>"
        # path.write_text(summary_str, encoding="utf-8")

        # msg = f"\n  Generated friendly summary: {path}"
        # plugin_utils.write_output(msg)
        pass
        # When implementing this, write a plugin utility to write the contents of the
        # friendly summary to file.
