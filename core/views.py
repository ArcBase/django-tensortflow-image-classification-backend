

from django.shortcuts import render
# Create your views here.
import io
#Rest framework for interacting with frontend and third party services
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from rest_framework.generics import (ListAPIView, RetrieveAPIView ,
                                ListCreateAPIView, DestroyAPIView , ListCreateAPIView)
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST 
from rest_framework.authentication import (SessionAuthentication, BasicAuthentication, TokenAuthentication)
from rest_framework.parsers import (MultiPartParser, FormParser)
from rest_framework.decorators import parser_classes

#Prcoesses and handle files
from django.core.files.storage import FileSystemStorage

import numpy as np

#Deep Learning Libaries
import tensorflow as tf
import json
from tensorflow import Graph
from keras.models import load_model
from keras.preprocessing import image


#loads image classes from json file

with open('./models_store/imagenet_classes.json','r') as f:
    labelInfo=f.read()

#label info
labelInfo=json.loads(labelInfo)

#Launch a Graph 
modelGraph = Graph()
with modelGraph.as_default():
    #initailizes a session
    tf_session = tf.compat.v1.Session()
    with tf_session.as_default():
        model=load_model('./models_store/MobileNetModelImagenet.h5')
        if model:
            print('works')

from django.core.files import File

height , width =224,224
class ProcessImage(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        try:
            data = request.data
            uploadedImage =  data['imageFile']
            # f = open(uploadedImage)
            # myfile = File(f)

            if data['imageFile'] != None:
                print(uploadedImage)
                
                fs=FileSystemStorage()

                filePathName=fs.save(uploadedImage.name,uploadedImage)
                filePathName=fs.url(filePathName)
                testimage='.'+filePathName
                #Kerasz
                theImage =  image.load_img(testimage,target_size= (height ,width)) 

                #converts to nump array
                image_x = image.img_to_array(theImage)

                image_x = image_x/255 
                image_x = image_x.reshape(1,height, width,3)

                #Tensorflow comes in here , finally
                with modelGraph.as_default():
                    #uses the tensorflow session
                    with tf_session.as_default():
                        #predicts image from the model
                        prediction  = model.predict(image_x)
                        
                #Gets the highest the value from the model preditcion
                result = np.argmax(prediction[0])

                #renders the result
                the_result_label = labelInfo[str(result)]

                print(the_result_label[1])

                context = {
                    'Message':'Image Uploaded',
                    'Label':the_result_label[1]
                }

                fs.delete(uploadedImage.name)
                return Response(data  = context , status= HTTP_200_OK)
            else:
                context = {
                    'Message': 'Come on buddy, upload an image'
                }

                return Response(data  = context , status= HTTP_200_OK)


        except Exception as e:
            print('Failed')
            print(e)
            messsage = {
                'Message':'Error Returning Result'
            }
            return Response(data= messsage , status= HTTP_400_BAD_REQUEST)

