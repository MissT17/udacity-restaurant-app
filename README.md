# Restaurant Project Description
This webapp is designed to display a list of restaurants with their respective menus and menu items available at the moment. The app allows the users to add, edit and delete restaurants as they wish.

## Directory Structure
In the GitHub …… repository you will find the following files:
1. *finalproject.py* – contains all the logic of the app in terms of user authorization and content
2. *login.py* - contains the logic in relation to the user authentication via Google or Facebook APIs
3. *static* folder – contains all the files necessary for the styling of the application, including bootstrap library, jquery, javascript and custom css.
4. *templates* folder – contains all the .html code for all the pages that allow the users to view/edit/delete the content of the app
5. *database_setup* file – contains the app database description
6. *client_secret_new.json* & *fb_client_secrets.json* - should contain the client secrets from Google and Facebook respectively necessary for the API usage
7. *json_format.py* - explains the serialization logic for JSON endpoints 
8. *restaurantmenu_fn_user.db* & *restaurantmenu_fn.db* - two databases necessary for the app 
9. *README.md*

## Requirements
- Please make sure that you have a 2.7 version of Python installed on your machine as the code is optimized for this version of Python. You will also need to install the Vagrant environment. Please follow the instruction on Vagrant installation [here](https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/348776022975461/lessons/3967218625/concepts/39636486110923).
- In order to be able to test all the features of the application, you will also need Google and Facebook API keys. If you do not yet have a developer Google and Facebook accounts, please follow the instructions on how to open them below:
    - Google account[here](https://developers.google.com/identity/sign-in/web/devconsole-project) (enable a Google+ API and indicate `http://localhost:5000/login`as 'Authorised JavaScript origins' and
`http://localhost:5000/gconnect` as 'Authorised redirect URIs') > download JSON and save as *client_secret_new.json* file
    - Facebook [here](https://developers.facebook.com/docs/pages/getting-started/) > open your app's dashboard and save the app ID as well as the app secret in *fb_client_secrets.json*

## Installation
1. Clone the Github repository
    ```
    git clone https://github.com/MissT17/udacity-restaurant-app.git <optional folder name>
    ```
2. Move *fb_client_secrets.json* and *client_secret_new.json* into the cloned repository
3. Open */templates/login.html* > line 49, insert your Facebook appId > save the file
4. In the same */templates/login.html* > line 101, insert the Google client-id into the `data-clientid` attribute >save file
5. Open the terminal on your machine > navigate into the App_project folder > launch the vagrant environment `vagrant up` > `vagrant ssh`> `python finalproject.py`
6. A webpage will be launched in the default browser under localhost:5000/
7. You can now navigate the website and test it

## Expected Outcome
The app is thought as a dynamic environment that allows its users to constantly improve and edit the content of the app. On login (either via Google or Facebook) the user gets access to the whole content of the app and is able to edit/delete the content (restaurant names, menus, menu items, their descriptions, etc.) that he/she previously created. In order to either add, edit or delete the content the user has to fill out the form and confirm the action. All users are allowed to add new restaurants at any point in time. Once the restaurant is created, only its creator has the right to edit or delete it. In a logged out session, the users have the possibility only to consult the content of the website.

## License:
The photos are taken from http://kaboompics.com/[http://kaboompics.com/ and are available according to kaboompics own license[https://kaboompics.com/page/license-and-faq] for free use with the exception of redistribution.