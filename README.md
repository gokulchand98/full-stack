# Sportswear Store 
### Gokulchand
-A Project in  Udacity Full Stack Development [FSND Course](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

### Overview Of The Store:
The Online Sportswear store is a web app in which there are items categorized by the type of sport and one can find all the wearables related to that sport in this store.Everyone can see these items but only the authorized persons can create, edit, delete the items. 

### Why This Project?
This web application is useful to the sport person ,athletes and even to the common people.
A variety of functions, amazing features and utilities  but deep down, it’s  all just creating, reading, updating and deleting data. In this project,knowledge of building dynamic websites with persistent data storage and creating a web application that provides a compelling service to your users is mainly focussed.

### Things Learnt By This Project:
  * Developing RESTful web application using the Python framework Flask.
  * Implementing  third-party OAuth authentication.
  * Implementing CRUD (create, read, update and delete) operations on the database.

## Prerequistic Skills:
1. Python
2. HTML
3. CSS
4. OAuth
5. Flask Framework
6. flask_sqlalchemy
7. Bootstrap

### Prerequisites:
* Python 
* Vagrant
* VirtualBox

### Project Setup:
1. Install VirtualBox and Vagrant
2. Clone the repo
3. Unzip and place the Item Catalog folder in your Vagrant directory
4. Launch Vagrant


#### Steps to Run:
  1. Opening Git bash from Vagrant
  2. Launching Vagrant :
  `
    $ vagrant up
  `
  3. Logging into Vagrant :
  `
    $ vagrant ssh
  `
  4. Moving  to the server side vagrant folder :
  `
    $ cd /vagrant
  `
  5. Moving to Project folder ie Sportswear :
  `
    $ cd Sportswear
  `
  6. Running the project :
  `
    $ python final_catalogue.py
  `
  7. Open any browser(Google Chrome,Internet Explorer,Firefox...),type URL:
  [http://localhost:5000/home](http://localhost:5000/login).
  ### JSON end points
  In this application, json end points are created for multi purpose using REST architecture 
#### urls:
`
http://localhost:5000/sportscat/json
`
`
http://localhost:5000/sports/JSON
`
`
http://localhost:5000/category/1/items.json
`


