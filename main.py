#!/usr/bin/env python
import os
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db

#Data store model
class GeoLocation(db.Model):
    user = db.UserProperty()
    date = db.DateTimeProperty(auto_now_add = True)
    #GeoPt object which stores Latitude and Longitude
    position = db.GeoPtProperty()
    address = db.PostalAddressProperty()
    header = db.TextProperty()

class MainHandler(webapp2.RequestHandler):
    #Class Variables: To be passed as template values
    admin_str = ''
    geo_str = ''
    loginout_str = ''
    user_str = ''
    
    #GET method
    def get(self):
        
        #Check if the user has logged in (Google Account)
        user = users.get_current_user()
        if not user:
            #Create appropriate login/logout string for the template
            login_url = users.create_login_url(self.request.url)
            #self.loginout_str = '<a href="' + login_url + '">Login</a>'
            self.loginout_str = ''
            
            #Ask the user to login if he wants personalized results.
            self.geo_str = '<center><p>Please <a href="' + login_url + '">login here</a> with your Google Account to enjoy personalized geo-location based services.</p></center>'
        else:
            #Create appropriate login/logout string for the template
            logout_url = users.create_logout_url(self.request.url)
            self.loginout_str = '<a href="' + logout_url + '">Logout</a>'
            
            #If the user is admin generate Admin Area Link string
            if users.is_current_user_admin():
                self.admin_str = '<a href="/admin/">Admin Area</a> |'
            
            #Welcome string for the user (his e-mail ID for now)
            self.user_str = '<p>Hello, ' + user.email() + '</p>'
            
            #Selective JavaScript html to be pasted if the user has logged in.
            self.geo_str = """<!-- Geo-Coding JavaScript start -->
        <center>
        <p id="geoloc"><img height="50px" width="50px" src="static/loading.gif" alt="Loading ..." />
        <br>Waiting for your permission/Processing ...</p>
        </center>
        <script src="static/jquery-min.js" type="text/javascript" charset="utf-8"></script>
        <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>
        <script src="http://code.google.com/apis/gears/gears_init.js" type="text/javascript" charset="utf-8"></script>
        <script src="static/geo-min.js" type="text/javascript" charset="utf-8"></script>            
        <script type="text/javascript" src="static/main.js"></script>
        <!-- Geo-coding JavaScript End -->"""
        
        #templating and rendering using the above variables
        template_values = {
                           'loginout_str' : self.loginout_str,
                           'geo_str' : self.geo_str,
                           'user_str' : self.user_str,
                           'admin_str' : self.admin_str
                           }
        file_path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        html = template.render(file_path, template_values)
        self.response.out.write(html)
#Class MainHandler End

#When a user posts the data to the server this handles the request
class StoreHandler(webapp2.RequestHandler):
    def post(self):
        gstore = GeoLocation(parent = None)
        gstore.user = users.get_current_user()
        gstore.position = db.GeoPt(float(self.request.get('lat')), float(self.request.get('long')))
        gstore.header = db.Text(str(self.request.headers))
        address = self.request.get('address')
        gstore.address = db.PostalAddress(address)
        gstore.put()
#Getting the values from POST request header and inserting them into the DataStore
#End of StoreHandler class

#Admin Area class: Shows the last 100 peoples' information
#as a table
class AdminHandler(webapp2.RequestHandler):
    
    #Again some class variables to handle template values
    loginout_str = ''
    admin_str = ''
    query_dict = None
    
    #Get method
    def get(self):
        
        #See if the user has logged in
        user = users.get_current_user()
        if user:
            #Double check if the user is an administrator
            if users.is_current_user_admin():
                
                #Create appropriate login/logout url
                logout_url = users.create_logout_url(self.request.url)
                self.loginout_str = '<a href="' + logout_url + '">Logout</a>'
            
                #Admin Area Login Link (Not necessary)
                if users.is_current_user_admin():
                    self.admin_str = '<a href="/admin/">Admin Area</a> |'
                
                #Query the datastore for the last 100 entries from the dataModel
                #named 'GeoLocation', there are no ancestors for this datastore (no namespaces)
                self.query_dict = db.GqlQuery("SELECT * FROM GeoLocation ORDER BY date DESC LIMIT 100")
                
                #the regular templating follows this code
                template_values = {
                            'table' : self.query_dict,
                           'loginout_str' : self.loginout_str,
                           'admin_str' : self.admin_str
                }
                
                file_path = os.path.join(os.path.dirname(__file__), 'templates/admin.html')
                html = template.render(file_path, template_values)
                self.response.out.write(html)
                
            else:
                self.response.out.write('Your\'e not an administrator!')
        else:
            self.response.out.write('Please <a href="' + users.create_login_url() + '">Login</a> here')

app = webapp2.WSGIApplication([('/store',StoreHandler),('/', MainHandler),('/admin/.*', AdminHandler)], debug=True)