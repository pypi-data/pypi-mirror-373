import subprocess, sys, pkg_resources, os
from conda import plugins
from conda.base.context import context
from dataflow.models import LocalEnvironment
from dataflow.db import get_local_db
from datetime import datetime, timezone
from dataflow.utils.logger import CustomLogger

logger = CustomLogger().get_logger(__name__)

def is_local_environment(target_prefix):
    """Check if the environment is a local user environment."""
    return (
        os.environ.get('HOSTNAME') is not None and 
        target_prefix and 
        target_prefix.startswith('/home/jovyan')
    )

def save_environment_to_db(env_name: str, status: str = "Created"):
    """Save environment information to LocalEnvironment table."""
    try:
        db_generator = get_local_db()
        db = next(db_generator)
        
        # Check if environment already exists
        existing_env = db.query(LocalEnvironment).filter_by(name=env_name).first()
        if existing_env:
            # Update status if environment exists
            existing_env.status = status
            existing_env.updated_at = datetime.now(timezone.utc)
            db.commit()
            return
        
        # Create new LocalEnvironment record
        local_env = LocalEnvironment(
            name=env_name,
            status=status,
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(local_env)
        db.commit()
        
    except Exception as e:
        print("Error saving environment! Please try again after deleting the environment")
        logger.error(f"Error saving environment to database: {str(e)}")
    finally:
        db_generator.close()

def install_deps(command: str):
    """Install dataflow dependencies."""
    target_prefix = context.target_prefix
    args = context._argparse_args
    env_name = os.path.basename(target_prefix) if target_prefix else None

    should_save_to_db = is_local_environment(target_prefix) and env_name

    try:
        if (args.get('clone') is not None):
            if should_save_to_db:
                save_environment_to_db(env_name, "Created")
            return
        
        install_dataflow_deps = pkg_resources.resource_filename('plugin', 'scripts/install_dataflow_deps.sh')
        process = subprocess.Popen(
            ["bash", install_dataflow_deps, target_prefix],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
            sys.stdout.flush()
        
        return_code = process.wait()
        if return_code != 0:
            print(f"Error in creating environment!!")
            if should_save_to_db and env_name:
                save_environment_to_db(env_name, "Failed")
        else:
            if env_name and should_save_to_db:
                save_environment_to_db(env_name, "Created")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}\nPlease delete the environment and try again.")
        logger.error(f"Error installing dependencies: {str(e)}")
        if should_save_to_db and env_name:
            save_environment_to_db(env_name, "Failed")

def remove_environment_from_db(env_name: str):
    """Remove environment information from LocalEnvironment table."""
    try:
        db_generator = get_local_db()
        db = next(db_generator)
        
        # Find and delete the environment
        existing_env = db.query(LocalEnvironment).filter_by(name=env_name).first()
        if existing_env:
            db.delete(existing_env)
            db.commit()
        else:
            logger.warning(f"Environment '{env_name}' not found in database")

    except Exception as e:
        print(f"Error removing environment! Please delete from the dataflow enviornment page")
        logger.error(f"Error removing environment from database: {str(e)}")
    finally:
        db_generator.close()

def package_operations(command: str):
    """Track conda install/remove/update commands for packages and update libraries in database."""
    target_prefix = context.target_prefix
    env_name = os.path.basename(target_prefix) if target_prefix else None

    # to catch env removal
    if not os.path.exists(target_prefix):
        if is_local_environment(target_prefix) and env_name:
            remove_environment_from_db(env_name)
        return

    should_update_db = is_local_environment(target_prefix) and env_name

    if should_update_db:
        try:
            db_generator = get_local_db()
            db = next(db_generator)
            
            # Find the environment and set need_refresh to True
            existing_env = db.query(LocalEnvironment).filter_by(name=env_name).first()
            if existing_env:
                existing_env.need_refresh = True
                existing_env.updated_at = datetime.now(timezone.utc)
                db.commit()
            
        except Exception as e:
            logger.error(f"Error updating need_refresh in database: {str(e)}")
        finally:
            db_generator.close()

@plugins.hookimpl
def conda_post_commands():
    yield plugins.CondaPostCommand(
        name=f"install_deps_post_command",
        action=install_deps,
        run_for={"create", "env_create"},
    )
    yield plugins.CondaPostCommand(
        name=f"package_operations_post_command",
        action=package_operations,
        run_for={"install", "remove", "update"},
    )