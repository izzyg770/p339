"""Insta485 model (database) API."""
import flask
import ccp


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_all_pets():
    """Get all pets from DB."""
    connection = ccp.model.get_db()
    cur = connection.execute(
        "SELECT * FROM pets"
    )
    return cur.fetchall()


def get_one_pet(name):
    """Get one pet from DB."""
    connection = ccp.model.get_db()
    cur = connection.execute(
        "SELECT * FROM pets "
        "WHERE username=?",
        (name, )
    )
    return cur.fetchone()


def create_pet(name, likes):
    """Create pet in DB."""
    connection = ccp.model.get_db()
    connection.execute(
        "INSERT INTO pets(name, likes) "
        "VALUES (?, ?)",
        (name, likes)
    )
    connection.commit()
    new_pet = {"name": name, "likes": likes}
    return new_pet

