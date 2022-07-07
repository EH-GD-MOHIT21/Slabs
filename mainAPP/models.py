from django.utils.text import slugify
from django.db import models
from users.models import User
from django.utils import timezone
# Create your models here.

class Playground(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=40)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField()


    def save(self,*args,**kwargs):
        self.date_updated = timezone.now()
        super(Playground,self).save(*args,**kwargs)




class Problem(models.Model):
    url = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    statement = models.TextField()
    author = models.ForeignKey(User,on_delete=models.Case)
    total_submissions = models.IntegerField(default=0)
    total_success_submissions = models.IntegerField(default=0)
    published = models.BooleanField(default=False)
    difficulty = models.CharField(max_length=10,default='easy')
    points = models.FloatField(default=10)


    def unique_slug_generator(self):
        slug = slugify(self.title)  
        return slug + "-" + str(self.id)


    def save(self,*args,**kwargs):
        self.url = self.unique_slug_generator()
        super(Problem,self).save(*args,**kwargs)




class TextCase(models.Model):
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
    inputs = models.TextField()
    output = models.TextField()



class Problem_Rating(models.Model):
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)
    rating_value = models.FloatField(default=0)
    user = models.ForeignKey(User,on_delete=models.Case)



class UserSubmission(models.Model):
    # can not be editable model
    user = models.ForeignKey(User,on_delete=models.Case)
    code = models.TextField()
    submission_time = models.DateTimeField(auto_now_add=True)
    problem = models.ForeignKey(Problem,on_delete=models.Case)