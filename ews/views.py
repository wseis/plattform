from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import BathingSpotForm, SiteForm, FeatureDataForm, PredictionModelForm, SelectAreaForm
from .models import BathingSpot, Site, FeatureData, FeatureType, User, PredictionModel, SelectArea
from django.urls import reverse
from tablib import Dataset, core
from .resources import FeatureDataResource
from django.contrib.auth.decorators import login_required
import numpy as np
import pandas as  pd
from django.db import IntegrityError
import plotly.express as px
from plotly.offline import plot
from django_pandas.io import read_frame
# Create your views here.


@login_required
def bathingspots(request):
    entries = Site.objects.filter(owner = request.user, feature_type = FeatureType.objects.get(name = 'BathingSpot'))

    return render(request, "ews/index.html", {"entries": entries})

@login_required
def sites(request):
    sites = Site.objects.filter(owner = request.user)
    return render(request, "ews/sites.html", {"entries": sites})#,"item": "spot"})

@login_required(login_url="login")
def mlmodels(request):
    mlmodels = PredictionModel.objects.filter(user = request.user)
    return render(request, "ews/models.html", {"entries": mlmodels})

@login_required
def model_config(request):
    if request.method == "POST":
        form = PredictionModelForm(request.user, request.POST)
        if form.is_valid():
            pmodel = PredictionModel()
            pmodel.user = request.user
            pmodel.name = form.cleaned_data["name"]
            #pmodel.bathing_spot=form.cleaned_data["bathing_spot"]
            pmodel.save()
            pmodel.site.set(form.cleaned_data["site"])
            pmodel.area.set(form.cleaned_data["area"])
            pmodel.save()
            return HttpResponseRedirect(reverse("ews:mlmodels"))
        else:
            return HttpResponse(request, "Form not valid")

        return HttpResponseRedirect(reverse("ews:mlmodels"))
    else:
        pmodel_form = PredictionModelForm(request.user)
        return render(request, "ews/model_config.html", {"pmodel_form": pmodel_form})

def model_edit(request, model_id):
    model = PredictionModel.objects.get(id = model_id)
    return render(request, 'ews/sites.html', {"entries": model.site.all(), 'areas': model.area.all()})


@login_required
def spot_create(request):
    if request.method == "POST":
        form = BathingSpotForm(request.POST)
        user = request.user
        if form.is_valid():
            spot = BathingSpot()
            spot.name = form.cleaned_data["name"]
            spot.description = form.cleaned_data["description"]
            spot.user = user
            spot.save()
        return HttpResponseRedirect(reverse('ews:bathing_spots'))
    else:
        form = BathingSpotForm()          
    return render(request, "ews/create.html", {"form":form})




@login_required
def detail_view(request, spot_id):
    entries = BathingSpot.objects.get(id = spot_id)
   #sites = entries.sites.values()
    #featuretype = []
    
    #for i in range(len(sites)):
      #  sites[i]["feature_type"] = FeatureType.objects.get(id = sites[i]['feature_type_id'])
    
    return render(request, "ews/detail.html", {"entries": entries}) #, "sites":sites})


@login_required
def add_site(request):
    new_site = Site()
    if request.method == "POST":
        form = SiteForm(request.POST)
       # form.owner=request.user
        if form.is_valid():
            
            new_site.name=form.cleaned_data["name"]
            new_site.feature_type=form.cleaned_data["feature_type"]
            
            new_site.owner=request.user
            new_site.save()
            new_site.bathing_spot.set(form.cleaned_data["bathing_spot"])
            new_site.save()

        return HttpResponseRedirect(reverse('ews:sites'))
    else:
        # prepopulating with dictionary
        form = SiteForm()
        user_id = User.objects.filter(username=request.user).values()[0]["id"]
        spot= BathingSpot.objects.filter(user = user_id) 
    return render(request, "ews/add_site.html", {"form":form, "spot":spot})

def delete_site(request, site_id):
    Site.objects.get(id=site_id).delete()
    return HttpResponseRedirect(reverse('ews:sites'))

def delete_model(request, model_id):
    PredictionModel.objects.get(id=model_id).delete()
    return HttpResponseRedirect(reverse('ews:mlmodels'))




@login_required
def add_data(request):
    if request.method == "POST":
        form = FeatureDataForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('ews:add_site'))
    else:
        form = FeatureDataForm()
        
    return render(request, "ews/add_data.html", {"form":form})

#def delete_site(request, site_id):
#    site.objects.filter(id=site_id).delete()
 #   return render(request, )

#@login_required
@login_required
def file_upload(request, site_id):
    if request.method == 'POST':

        feature_resource = FeatureDataResource()
        dataset = Dataset()
        new_data = request.FILES['myfile']


        imported_data = dataset.load(new_data.read().decode("utf-8"), format="csv")
        #create an array containing the location_id
        location_arr = [site_id] * len(imported_data)

        # use the tablib API to add a new column, and insert the location array values
        imported_data.append_col(location_arr, header="site")

        try:
            result = feature_resource.import_data(dataset, dry_run=True)  # Test the data import
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)

        if not result.has_errors():
            feature_resource.import_data(dataset, dry_run=False)  # Actually import now
        
        return HttpResponseRedirect(reverse("ews:site_detail",    args=[site_id,]))
    return render(request, 'ews/import.html', {"site_id":site_id})


@login_required
def site_detail(request, site_id):
        df = read_frame(FeatureData.objects.filter(site_id=site_id))
        entry = Site.objects.get(id = site_id)
        fig = px.bar(df, "date", "value",  opacity = 1)
        fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.6)
        
        #fig.update_layout(title_text=df.site[0].replace("_", " "))
        fig = plot(fig, output_type = "div")
        
        return render(request, "ews/site_detail.html", {"fig":fig, "entry":entry})#, "data":df.to_html()})
    
@login_required
def selectarea_create(request):
    if request.method == "POST":
        form = SelectAreaForm(request.POST)
        if form.is_valid():
            selectarea = SelectArea()
            selectarea.name = form.cleaned_data["name"]
            selectarea.geom = form.cleaned_data["geom"]
            
            selectarea.feature_type = form.cleaned_data["feature_type"]
            selectarea.save()
            return HttpResponseRedirect(reverse("ews:selectarea_create"))
        else:
            return HttpResponse("Submission not successfull")
    else:
        form = SelectAreaForm()
        entries = Site.objects.all()
        areas = SelectArea.objects.all()
        return render(request, 'ews/selectarea_create.html', {'form': form, 'areas':areas, 'entries': entries})


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "ews/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "ews/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("ews:mlmodels"))
    else:
        return render(request, "ews/register.html")


import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from shapely.geometry import shape, Point
import statsmodels
from sklearn.model_selection import GridSearchCV, train_test_split
import pickle

def model_fit(request, model_id):
    model = PredictionModel.objects.get(id = model_id)
    areas = read_frame(model.area.all())
    areavars = []
    for index1, row1 in areas.iterrows():
        df = read_frame(Site.objects.filter(feature_type = FeatureType.objects.get(name=row1["feature_type"])))
        polygon = shape(row1["geom"])
        select = []
        
        for index2, row2 in df.iterrows():
            select.append(polygon.contains(shape(row2['geom'])))
        data = read_frame(FeatureData.objects.filter(site__in = df[select]['id']), index_col = "date")
        data["area"] = row1["name"]
        data["feature_type"] = row1["feature_type"]
        areavars.append(data)
    lagvars = []

    for i in range(len(areavars)):
        ft = areavars[i].area.unique()+ " " +areavars[i].feature_type.unique()
        d = areavars[i].pivot(columns = 'site', values = 'value')
        if len(d.columns) > 1:
            d = pd.DataFrame(d.mean(axis = 1, skipna = True))
        for j in [1, 2, 3, 4, 5]:
            df = pd.DataFrame()
            df[ft + '_shift_'+ str(j)] = d.rolling(window=j).mean().shift(1)
            lagvars.append(df)
            
    res = pd.concat(lagvars, axis = 1)
    res = res[res.index.month.isin([5, 6, 7, 8, 9])].reset_index()
    rain_cols = [col for col in res.columns if 'Rainfall' in col]
    res[rain_cols] = res[rain_cols].add(1).apply(np.log)

    FIB = read_frame(FeatureData.objects.filter(site = model.site.all()[0]))
    FIB["date"] = FIB.date.round("D")
    d = FIB.merge(res, on= "date").drop("variable", axis = 1)
    D = d.dropna()
    y = np.log10(D["value"])
    X = D.drop(["date", "value", "id", "site"], axis = 1)
    
    
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=4)

    if model.fit == None:

        grid = {'n_estimators':[1000], 'max_depth': np.linspace(1, 6, 6), 'max_features': [4,6,8],  'min_samples_leaf':[1]} 
    
        # Instantiate the Random regressor: elastic_net
        rf = RandomForestRegressor()

        # Setup the GridSearchCV object: gm_cv
        gm_cv = GridSearchCV(rf, param_grid=grid, cv = 5)

        # Fit it to the training data

        gm_cv.fit(X_train, y_train)
        rf = RandomForestRegressor(n_estimators = gm_cv.best_params_["n_estimators"],
                            max_depth = gm_cv.best_params_["max_depth"],
                            max_features = gm_cv.best_params_["max_features"],min_samples_leaf=1)
        rf.fit(X_train, y_train)
        model.fit = pickle.dumps(rf)
        model.save()
    
    rf = pickle.loads(model.fit)
    # Predict on the test set and compute metrics
    #y_pred1 = gm_cv.predict(X_test)
    y_pred = rf.predict(X_test)


    #r2 = rf.score(X_test, y_test)
    #r2_in = rf.score(X_train, y_train)

    #mse = mean_squared_error(y_test, y_pred)
    #mse_in = mean_squared_error(y_train, rf.predict(X_train))

    df_test = pd.DataFrame({'meas': y_test, 'pred': rf.predict(X_test), 'split': 'out of sample'})
    df_train = pd.DataFrame({'meas': y_train, 'pred': rf.predict(X_train), 'split': 'in sample'})
    df = pd.concat([df_test, df_train])

    fig = px.scatter(df, x = "meas", y = "pred", color = "split", 
                 color_discrete_sequence=['#212c52','#75c3ff'])

    fig.update_layout(
        font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        title = {'text':'Model fit of Random Forest model'},
        xaxis_title = "measured data (sample)",
        yaxis_title = "fitted values (in sample fit)",
        #markersize= 12,
        )
    fig.update_layout(legend=dict(
    yanchor="top",
    title=None,
    y=0.99,
    xanchor="left",
    x=0.01
    ))
    fig.update_traces(marker_size = 8)#['#75c3ff', "red"],#, marker_line_color='#212c52',
 #                 marker_line_width=1.5, opacity=1)

    model_fit = plot(fig, output_type = "div")



    importances = pd.Series(data=rf.feature_importances_,
                        index= X.columns)

        # Sort importances
    importances_sorted = importances.sort_values()
    importances_df = importances_sorted.reset_index()
    importances_df.columns = ["feature", "importance"]
    fig = px.bar(importances_df, y="feature", x="importance", orientation='h'    )

    fig.update_layout(
            font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
            font_color="black",
            title = {'text':'Feature importance of Random Forest model'}
            #markercolor = "#212c52"
        
        )
    fig.update_traces(marker_color='#75c3ff', marker_line_color='#75c3ff',
                        marker_line_width=1.5, opacity=1)

    feature_importance = plot(fig, output_type = "div")
    bathingspot= model.site.all()[0]    

    return render(request, 'ews/model_fit.html', {'bathingspot':bathingspot, "entries": Site.objects.all(), "model": model, 'areas': model.area.all(),'model_fit':model_fit, 'feature_importance':feature_importance})


@login_required
def prediction_switch(reuqest, model_id):
    model = PredictionModel.objects.get(id = model_id)
    model.predict = not model.predict
    model.save()
    return JsonResponse({"status": str(model.predict)}, status=201)

#import pickle
#from ml.models import MlModels
#from rest_framework.response import Response


# using the model
#@api_view(['GET'])
#def predict(request):
#    if request.method == "GET":
 #       X = [[0.12, 22, 33, 100]]
 #       raw_model = MlModel.objects.all()[0]
 #       model = pickle.loads(raw_model.model)
 #       print(model.predict(X))
 #       return Response(status=status.HTTP_200_OK)

#from sklearn import svm
#import pickle
#from ml.models import MlModels
#from rest_framework.response import Response

# Saving the model
#@api_view(['GET'])
#def save(request):
#  if request.method == 'GET':
#    X = [[0.12, 22, 33, 100], [0.19, 19, 99, 33], [0.5, 50, 150, 0]]
#    y = [1, 0, 1]
#    model = svm()
#    model.fit(X=X, y=y)
#    data = pickle.dumps(model)
#    MlModels.objects.create(model=data)
#    return Response(status=status.HTTP_200_OK)