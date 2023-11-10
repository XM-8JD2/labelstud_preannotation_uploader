# labelstud_preannotation_uploader
Import pre-annotations output by YOLOv5 into LabelStud via the LabelStud API.

Instructions:
1. Make yolo save the reasoning as a file using a format similar to this
`python detect.py --weights "modelPath" --source "contentPath" --save-txt`

2. Import the image into a project of LabelStud, remember the name of the project, and select the template as "Object Detection with Bounding Boxes".

3. Place `labelstud_preannotation_uploader_3.py` in a directory with the following structure:
```
root
-labelstud_preannotation_uploader_3.py
-notes.json
--labels
--dataName1.txt
--dataName2.txt
--dataName3.txt
...
```


dataName.txt:
```
1 0.000000 0.000000 0.000000 0.000000
2 0.000000 0.000000 0.000000 0.000000
3 0.000000 0.000000 0.000000 0.000000
```

notes.json (export the project in LabelStud to YOLO data set format to obtain):
```
{
   "categories": [
     {
       "id": 0,
       "name": "a1"
     },
     {
       "id": 1,
       "name": "a2"
     },
     {
       "id": 2,
       "name": "a3"
     }
   ],
   "info": {
     "year": 2023,
     "version": "1.0",
     "contributor": "Label Studio"
   }
}
```

4. Fill in the parameters of the main function in `labelstud_preannotation_uploader_3.py` as the parameters required in your use case (width, height) are the width and height of the data set image)
`main('you labelstud key','localhost:8080', 'you labelstud task name', 'width', 'height')`

---

limit:
- All data set files of list items must have the same length and width
- Unable to import confidence output from yolo


Done using ChatGPT3.5
