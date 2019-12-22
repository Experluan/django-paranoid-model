# django-paranoid-model
Django abstract model with paranoid behavior, therefore when an instance is deleted it is not really deleted from database, it's applied a mask on the filter so when filter, the result are the "undeleted" instances.

## Summary

1) **Get Started**
2) **Create you paranoid model**
3) **Instance Manipulate**
4) **Making queries**

--- 

# Get Started
Right now, there are two ways you can get paranoid model: 
1) clone this repository
2) Copy the files that allow paranoid behavior works

**1) Clone this repository**

To get the base class of a ``Paranoid``  model, import from Paranoid class from
```py
from [path to this repo].paranoid_model.models import Paranoid
```
Than you can make the inheritance like the example **Create you Paranoid Model**.

**2) Copy the files that allow paranoid behavior works**

Raw the files queryset.py, manager.py and models.py from app paranoid_model and paste on your local project. 

You can copy from this link:
* [queryset.py](https://github.com/DarknessRdg/django-paranoid-model/blob/master/paranoid_model/queryset.py)
* [manager.py](https://github.com/DarknessRdg/django-paranoid-model/blob/master/paranoid_model/manager.py)
* [models.py](https://github.com/DarknessRdg/django-paranoid-model/blob/master/paranoid_model/models.py)

Folder lin link: https://github.com/DarknessRdg/django-paranoid-model/tree/master/paranoid_model

---

# Create your Paranoid Model

On your models.py file import Paranoid class from paranoid_models.models file, then inheritance Paranoid class on your models

```py
from django.db import models
import paranoid_model.models 
# from paranoid_models import models DON'T DO THAT!
# it will override ' from django.db import models ' 
# and will get and error to access models.Field() 

class Person(paranoid_model.models.Paranoid):  # make an inheritance
    # all the default fields come with inheritance:
    # created_at
    # updated_at
    # deleted_at
    name = models.CharField(max_length=255)
```

* created_at is the field with creation date
* updated_at is the field with latest update date
* deleted_at is the field with deletion date, so when it is None it means it hasn't been deleted

---

# Instance Manipulate

ParanoidModel has some some differences on default Django methods.

### Save()

This method has no difference, it work just like Django's

```py
my_paranoid_instance = Paranoid()
my_paranoid_instance.save()
```

### Delete()

The **most important** method. This is why pararanoid model exists. When ``delete()`` an instance it should not be really deleted from database, but hide from user. 

The magic is in the attribute ``deleted_at``. When there is no date (deleted_at is None) it means it has not been deleted, but if has a date it means it has been deleted. So when we call delete(), it will set up the current date to delete_at field and save the instance, instead of deleted.  

**The delete works on *CASCADE*. So all the related objects will be soft deleted**

```py
instance = ParanoidModel.objects.create()
instance.delete()  # instance has the current date on the field deleted_at but it still saved on database 
instance.deleted_at is None
>> False

# but remember that this delete will do the same to every related instances like:
person = Person.objects.create(name='My Name')
for i in range(5):
    Phone.objects.create(phone='123456789', owner=person)

person.delete()  # this will soft delete person
# but will also delete all the 5 phones related to this person
```

### Delete(hard_delete=True)

If you really wants to delete the instance from databse you can use parameter ``hard_delete``. It calls Django's default method

```py
instance = ParanoidModel.objects.create()
intance.delete()  # will soft delete
instance.delete(hard_delete=True)  # will call django delete, so will delete from database
```

Be careful using ``hard_delete``

### is_soft_deletd

This is a @property that returns a boolean if current instance has been soft deleted or not. Otherwise, it returns if attribute deleted_at is None. It is just a more easy way to check if deleted_at is None instead of use this whole sentence to check.

So you can just do the following:

```py
instance = ParanoidModel.objects.create()

instance.is_soft_deleted
>> False

instance.delete()
instance.is_soft_deleted
>> True

# real example
person = Person.objects.create(name='My name')
person.delete()

if person.is_soft_deleted:
    person.restore()
```

### Restore()

Once an instance has been soft deleted, it can be easily undeleted with method restore()

```py
instance = ParanoidModel.objects.create()

instance.delete()
instance.is_soft_deleted
>> True

instance.restore()
instance.is_soft_deleted
>> False
```

---

# Making queries

In short, the queries are the same as django's queries. The difference is that by default behavior all the queries comes with 
not soft deleted.

To make a querry and include the deleted instance just need to give parameter ``with_deleted`` to the querry. This is a boolean parameter, so it can be True or False.

##### Obs: Soft deleted is a instance where the filed ``deleted_at`` is not None


### All()
```py
ParanoidModel.objects.all()  # will return all the instancnes that hasn't been soft deleted
ParanoidModel.objects.all(with_deleted=False)  # this will exclude the soft deleted
ParanoidModel.objects.all(with_deleted=True)  # will include the soft deleted
```

As you can see, ``.all()`` will return the same instances that ``all(with_deleted=False)``

**Obs on related_name queries:** when an instance has been soft deleted, the related_querry ``all()`` will return ``with_deleted=True`` by default, because if the instance has been soft deleted, I guess, it want's to be querried the deleted objects, BUT you can alway pass the parameter ``with_deleted`` and it will work as you wish.

It's something like this:
```py
person = Person.objects.create(name='person')
for i in range(20):
    phone = Phone.objects.create(phone='123', owner=person)
    if i % 2 == 0:
        phone.delete()

person.phones.all()  # will return all not soft deleted

person.delete()  # will delete all the phones that belongs to person

# since person has been deleted, a related_name querry will work a little different
person.phones.all()  # will return all and include the soft deleted
person.phones.all(with_deleted=True)  # will return all and include soft deleted
person.phones.all(with_deleted=False)  # will return all not soft deleted
```
The explanation why Paranoid Query does it, is because imagine we have a *person* and we have *2 phones related to that person*, and that *person has been soft deleted*, and by cascade person's phones also soft deleted.

Now imagine that in the future, that person wants a report of your datas once saved in database, so when we filter his data, we will need, also, his data deleted.

That is why paranoid query will include soft deleted when querring related_name with a soft delete instance.

### Filter()
```py
ParanoidModel.objects.filter(**kwargs)  # will return the filtered instancnes that hasn't been soft deleted
ParanoidModel.objects.filter(with_deleted=False, **kwargs)  # this will exclude the soft deleted
ParanoidModel.objects.filter(with_deleted=True, **kwargs)  # will include the soft deleted
```

As you can see, ``.filter(**kwargs)`` will return the same instances that ``filter(with_deleted=False, **kwargs)``

### Deleted_only()

To filter only deleted you must use ``deleted_only`` filter. Thats because ``filter`` override querry parameter ``deleted_at`` and change it.

```py
for i in range(20):
    instance = ParanoidModel.objects.create()
    
    if i % 2 == 0:
        instance.delete()

ParanoidModel.objects.deleted_only()  # only soft deleted_instance

# DON'T DO THAT
# 
# ParanoidModel.objects.filter(deleted_at__isnull=True)
# this param 'deleted_at__isnull' is overwritten by querry filter
# that's because every param wich starts with 'deleted_at' are removed
```

### Get()
```py
ParanoidModel.objects.get(**kwargs)  
# will retrun a single instance of the object that matches with the querry
```

Careful with get() method, because it can raise some errors.
The possible raises are: 
* **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance
* **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry
* **model.SoftDeleted**: will be raised if the instance has been soft deleted.

You can do the following:
```py
try:
    ParanoidModel.objects.get(pk=10)
except ParanoidModel.DoesNotExist:
    # The querry didn't find any instance with pk = 10
    pass
```
or
```py
try:
    ParanoidModel.objects.get(pk=10)
except ParanoidModel.SoftDeleted:
    # The querry found an instance, but it has been soft deleted
    # it means you need to querry with method get_deleted() or get_or_restore()
    pass
```

But, if you pay attention it doesn't allow you to get an instance that has been soft deleted. Don't worry, no need to cry! :sob: ``get_deleted`` and ``get_or_restore`` will save you!

### Get_deleted()
```py
ParanoidModel.objects.get_deleted(**kwargs)  
# will retrun a single instance of the object that matches with the querry
```

Careful with get_deleted() method, because it can raise some errors.
The possible raises are: 
* **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance
* **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry
* **model.IsNotSoftDeleted**: will be raised if the instance has not been soft deleted yet.

You can do the following:
```py
try:
    ParanoidModel.objects.get_deleted(pk=10)
except ParanoidModel.DoesNotExist:
    # The querry didn't find any instance with pk = 10
    pass
```
or
```py
try:
    ParanoidModel.objects.get_deleted(pk=10)
except ParanoidModel.IsNotSoftDeleted:
    # The querry found an instance, but it has not been soft deleted yet
    # it means you need to querry with method get()
    pass
```
### Get_or_restore()
This method will work just like Django's wiht a thiny difference, it will restore the instance if it has been soft deleted

```py
ParanoidModel.objects.get_or_restore(pk=10)
```

Like all get method, it can raises some exceptions:
* **model.DoesNotExist**: (Django) will be raised if the querry doesn't match to any instance
* **model.MultipleObjectsReturned**: (Django) will be raised if more than 1 instances matches with the querry

```py
try:
    ParanoidModel.objects.get_deleted(pk=10)
except ParanoidModel.DoesNotExist:
    # The querry didn't find any instance with pk = 10
    pass
```
or
```py
try:
    ParanoidModel.objects.get_deleted(name__icontains='a')
except ParanoidModel.MultipleObjectsReturned:
    # The querry found more than 1 instance
    pass
```

### Restore()
This method restore all the instances soft deleted int the current querry set. Look at the example bellow

```py
for i in range(20):
    ParanoidModel.objects.create()

ParanoidModel.objects.all().count() == 0
>> True

ParanoidModel.objects.all(with_deleted=True).restore()

ParanoidModel.objects.all().count() == 0:
>> False
ParanoidModel.objects.all().count() == 20:
>> True
```
