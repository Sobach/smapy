---
title: Document Center
---

How-to recieve access token to Odnoklassniki (_www.odnoklassniki.ru_).

## Registering application

1. Go to [devaccess](http://www.odnoklassniki.ru/devaccess) page. Login, if needed.

2. You need to read and agree with terms and conditions.

    ![Terms and conditions](https://dl.dropboxusercontent.com/u/81437006/smapy/token_ok_1.png)

3. After accepting you will see something like this:

    ![Now you are OK-developer](https://dl.dropboxusercontent.com/u/81437006/smapy/token_ok_2.PNG)

4. Now you can go to ["My applications"](http://www.odnoklassniki.ru/dk?st.cmd=appsInfoMyDevList) page and add your application (link "Add aplication")

5. On the next screen select "Outside Odnoklassniki" link (on the right):

    ![Select place for app](https://dl.dropboxusercontent.com/u/81437006/smapy/token_ok_3.PNG)

6. Fill in form. All fields are required, but because we are not going to publish our application in catalog - we can fill them arbitrary. E.g. "http://localhost/" for application link, "The best app ever" for description, and any img url for icon, avatar, and image fields. Click "Save".

7. Now you should recieve an e-mail with app id, public key and secret key.

8. After recieving e-mail it's time to ask for access rights. Write a mail to _oauth@odnoklassniki.ru_ with request for "valuable_access". Don't forget to specify your application ID, application name, your uid, login and email.

9. Ususally it takes time to get reply and access.

## Adding token to [[KeyChain]]

## Using token
