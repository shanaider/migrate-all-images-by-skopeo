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

def skopeo_run(images):

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
                with open('retry_failed.log', 'a') as f:
                    sys.stdout = f # Change the standard output to the file we created.
                    print(images)
                    sys.stdout = original_stdout # Reset the standard output to its original value
                f.close()

            retry_count +=1
        else:
            print("Success")
            original_stdout = sys.stdout # Save a reference to the original standard 
            with open('retry_success.log', 'a') as f:
                sys.stdout = f # Change the standard output to the file we created.
                print("Images:", images, ">> Success")
                sys.stdout = original_stdout # Reset the standard output to its original value
            f.close()
            break


def push_all_images():
    #Opening JSON file
    f = open('failed.log')

    for line in f:
        l, _ = line.split("\n")
    with open('failed.log') as f:
        lines = [line for line in f.read().splitlines()]
        for i in lines:
            skopeo_run(i)

#call function
push_all_images()
