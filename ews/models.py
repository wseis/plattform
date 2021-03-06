from django.db import models
from django.contrib.auth.models import User
from djgeojson.fields import PointField, PolygonField
# Create your models here.


class BathingSpot(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="bathing_spots")
    name = models.CharField(max_length= 64)
    description = models.CharField(max_length = 200, default = " ")
    def __str__(self):
        return f"{self.name}"

class FeatureType(models.Model):
    name = models.CharField(max_length=64)
    unit = models.CharField(max_length=64, null = True)
    def __str__(self):
        return f"{self.name}"

class Site(models.Model):
    name = models.CharField(max_length=64, unique=True)
    ref_name =  models.CharField(max_length=64, null = True )
    geom = PointField(null = True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="owner")
    feature_type = models.ForeignKey(FeatureType, on_delete=models.CASCADE, related_name="feature_type")
    
    def __str__(self):
        return f"{self.name.replace('_', ' ').capitalize()}"
    
    @property
    def popupContent(self):
      return '<a href="/site_detail/{}"><strong>{}</strong></a> <p> {}</p>'.format(
          self.id,
          self.name.replace('_', ' ').capitalize(),
          self.feature_type)
    @property
    def SiteType(self):
        return '{}'.format(self.feature_type)
#"{% url 'ews:site_detail' entry.id  %}"

class Variable(models.Model):
    name = models.CharField(max_length=255, null = True)
    abbreviation = models.CharField(max_length=6, null = True)
    description = models.CharField(max_length=255, null = True)
    def __str__(self):
        return f"{self.name}"


class FeatureData(models.Model):
    date = models.DateTimeField()
    value = models.DecimalField(max_digits=1000, decimal_places=3)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="site")
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE, null=True, related_name="variable")
    class Meta:
        unique_together = ('date', 'site','value',)
    


class SelectArea(models.Model):
    name = models.CharField(max_length=64, unique=True)
    geom = PolygonField()
    feature_type = models.ForeignKey(FeatureType, on_delete=models.CASCADE, related_name = "areas")
    @property
    def SiteType(self):
        return '{}'.format(self.feature_type)
    def __str__(self):
            return f"{self.name}"

class PredictionModel(models.Model):
    name = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name = "models")
    #bathing_spot = models.ForeignKey(BathingSpot, on_delete=models.CASCADE, related_name="models")
    site = models.ManyToManyField(Site, related_name = "models", null = True, blank = True)
    area = models.ManyToManyField(SelectArea, related_name = "models", null = True, blank = True)
    fit = models.BinaryField(null=True)
    predict = models.BooleanField(default= False)
    def __str__(self):
        return f"{self.name}"



#class MlModels(models.Model):

 #   model       =   models.BinaryField()



