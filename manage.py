# manage.py
from flask.cli import FlaskGroup
from app import app, db  # import your app and db objects
from flask_migrate import Migrate #, MigrateCommand

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create Flask CLI group
cli = FlaskGroup(app)

# Add db commands to the CLI
@cli.command()
def hello():
    print("Hello from manage.py")

if __name__ == "__main__":
    cli()