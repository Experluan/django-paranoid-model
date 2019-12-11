from faker import Faker
from paranoid_model.models import Person, Phone
"""
File wiht utils functions
"""


fake = Faker('en_US')


def isdeleted(obj):
    """
    Function to check if model instance is deleted
    Args:
        obj: instance os a paranoid Model
    Returns:
        bool(): if obj is soft deleted
    """
    return obj.deleted_at is not None


def all_list(iterable, key):
    """
    Method to check if all item in iterable pass the key
    Args:
        iterable: iterable with all objects
        key: function to apply on every object
    Returns:
        bool(): if all objects pass the key
    """
    return all([key(item) for item in iterable])


def any_list(iterable, key):
    """
    Method to check if all item in iterable pass the key
    Args:
        iterable: iterable with all objects
        key: function to apply on every object
    Returns:
        bool(): if any objects pass the key
    """
    return any([key(item) for item in iterable])


def get_person_instance():
    """
    Method to return an instance of a Person
    not saved on database
    Returns:
        Person()
    """
    return Person(name=fake.prefix() + fake.name())


def create_list_of_person(quantity_saved, quantity_deleted):
    """
    Method to create a list of person on database
    Args:
        quantity_saved: int with amount of instances to save
        quantity_deleted: int with amount of instances to save and then delete
    """
    for count in range(quantity_saved):
        person = get_person_instance()
        person.save()

    for count in range(quantity_deleted):
        person = get_person_instance()
        person.save()
        person.delete()


def get_phone_instace(owner):
    return Phone(phone=fake.phone_number(), owner=owner)