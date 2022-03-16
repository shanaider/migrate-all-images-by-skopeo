import subprocess
import requests
import json
import datetime
import sys

##Datetime
x = datetime.datetime.now()
created_at = x.strftime("%Y-%m-%d %H:%M:%S")

##Parameter
docker_registry_url = "docker-registry.apps.crp-dev.allianz"
docker_user = "xxxx.yyy@allianz.com"
docker_token = "YYYYYYYYYYYYYYY"

acr_url = "xxxx.azurecr.io"
acr_user = "acr-admin" 
acr_access_key = "XXXXXXXXXXXXXXXXX"

def get_catalog():

    payload={}
    headers = {
    'Authorization': 'Bearer {}'.format(docker_token),
    'Content-Type': 'application/json'
    }

    response = requests.request("GET", 'https://'+docker_registry_url+'/v2/_catalog', headers=headers, data=payload ,verify=False)
    data = response.content

    # write to file
    with open('images_name.json', 'wb') as f:
        f.write(data)
    f.close()

def get_tags():

    # Opening JSON file
    f = open('images_name.json')
    
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    
    # Iterating through the json
    # list
    for i in data['repositories']:
        #print(i)
        url = 'https://'+docker_registry_url+'/v2/{}/tags/list'.format(i)
        print(url)

        payload={}
        headers = {
            'Authorization': 'Bearer {}'.format(docker_token),
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload ,verify=False)
        data = response.json()

        s = ""

        if len(data["tags"]) <= 0:
            #s = i +"\n"
            continue # ignore all images without tag
        else:
            for j in data["tags"]:
                s+=i+":"+j+"\n"
        # write to file
        with open('all-images-with-tags-'+created_at + '.log', 'a') as f:
            f.write(s)
        f.close()

    # Closing file
    f.close()

def skopeo_run(images):

    #images = "maintenance/aws-nodeport-controller:latest"

    retry_count = 0
    while retry_count < 3:
        result = subprocess.run([
            'skopeo','copy',
            '--src-creds',docker_user+':'+docker_token ,
            '--src-tls-verify=false',
            '--dest-creds',acr_user+':'+acr_access_key,
            'docker://{}/'.format(docker_registry_url) + images,
            'docker://{}/'.format(acr_url) + images
            ])

        if result.returncode != 0:
            print("Failed")

            if retry_count == 2:
                original_stdout = sys.stdout # Save a reference to the original standard output
                with open('failed.log', 'a') as f:
                    sys.stdout = f # Change the standard output to the file we created.
                    print(images)
                    sys.stdout = original_stdout # Reset the standard output to its original value
                f.close()

            retry_count +=1
        else:
            print("Success")
            original_stdout = sys.stdout # Save a reference to the original standard 
            with open('success.log', 'a') as f:
                sys.stdout = f # Change the standard output to the file we created.
                print("Images:", images, ">> Success")
                sys.stdout = original_stdout # Reset the standard output to its original value
            f.close()
            break


def push_all_images():
    #Opening JSON file
    f = open ('all-images-with-tags-'+created_at + '.log')

    for line in f:
        l, _ = line.split("\n")
    with open('all-images-with-tags-'+created_at + '.log') as f:
        lines = [line for line in f.read().splitlines()]
        for i in lines:
            skopeo_run(i)

#call function
get_catalog()
get_tags()
push_all_images()
