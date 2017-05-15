
/* global $ */
/* global localStorage */
var app = angular.module('myApp', ['ngRoute']);




    app.config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider){
    $routeProvider
      .when('/', {
          templateUrl: '/static/sub/home.html',
          controller: 'homeCtrl'
        
      })
      .when('/dashboard', {
          
        templateUrl: '/static/sub/dashboard.html',
        controller: 'cardctrl'
      })
      .when('/about', {
          templateUrl: '/static/sub/about.html'
      })
      .otherwise ({
            redirectTo: '/'
          
      });
      
        $locationProvider.html5Mode({
          enabled: true
        });
    }]);
    
    app.controller('homeCtrl', function($scope, $location, $http, $route) {
    $scope.login = function() {
        
        $('#loading').show();
        
        $scope.user = JSON.stringify({'email': $scope.user.email, 'password': $scope.user.password });
        
        $http({
                method: 'POST',
                url: '/api/users/login', 
                data: $scope.user,
                headers: {'Content-Type': 'application/json;charset=UTF-8'}
            })
            .then(function (response) {

                var reply =response.data;
                var new_token= reply['information'].data.token;
                if(localStorage.getItem(reply['information'].data.user.id)==new_token){
                    $location.path('/dashboard');
                    alert('You have successfully been authenticated');
                }

                
                sessionStorage.currentUser=  reply['information'].data.user.id;
                sessionStorage.email= reply['information'].data.user.email;
                sessionStorage.fname= reply['information'].data.user.fname;
                sessionStorage.lname= reply['information'].data.user.lname;

                $location.path('/dashboard');
                $('#loading').hide();
            })
            .catch(function(error) {
                $('#loading').hide()
              alert(error.data.message, error.status);
              $location.path('/')
            });
           
    };
    
    $scope.register = function(){
      // $scope.user = JSON.stringify({''})
      $('#loading').show();
      $http({
          method: 'POST',
          url: '/api/users/register',
          data: JSON.stringify({'firstname': $scope.firstname, 'lastname': $scope.lastname, 'email': $scope.email, 'username': $scope.username, 'password': $scope.password, 'confirm-password': $scope.passwordc, 'hint': $scope.hint}),
          headers: {'Content-Type': 'application/json;charset=UTF-8'}
      })
      .then(function(response) {
          var reply = response.data;
          var authorization_token= reply['information'].data.token;
  
          sessionStorage.currentUser= reply['information'].data.user.id;
          sessionStorage.email= reply['information'].data.user.email;
          sessionStorage.fname= reply['information'].data.user.firstname;
          sessionStorage.lname= reply['information'].data.user.lastname;
        
         
         $location.path('/dashboard');
         $('#loading').hide();
         alert('You have successfully created a new account and have been signed-in');
         
         
        //   if (reply.message == "failed"){
        //       $route.reload();
        //       $('#loading').hide();
        //       alert("Registration failed. Please try again");
        //   } else {
        //       $location.path('/dashboard');
        //       $('#loading').hide();
        //       alert("You successfully registered.");
        //   }
          
      })
      .catch(function(error) {
          $('#loading').hide();
          alert(error.data.message);
        });
      
    };
    
    $('#login-form-link').click(function(e) {
    	e.preventDefault();
    	$("#login-form").delay(100).fadeIn(100);
     	$("#register-form").fadeOut(100);
    	$('#register-form-link').removeClass('active');
    	$(this).addClass('active');
    	e.preventDefault();
    });
    $('#register-form-link').click(function(e) {
    	e.preventDefault();
    	$("#register-form").delay(100).fadeIn(100);
     	$("#login-form").fadeOut(100);
    	$('#login-form-link').removeClass('active');
    	$(this).addClass('active');
    	e.preventDefault();
    });

    
    });

    app.controller('NavbarCtrl', function($scope, $auth) {
        $scope.isAuthenticated = function() {
          return $auth.isAuthenticated();
        };
    });
    
    app.controller('cardctrl', function($scope, $http, $route){
        

        var share = document.getElementById('share');
        
        $scope.currentUser = sessionStorage.currentUser;
        $scope.email = sessionStorage.email;
        $scope.fname = sessionStorage.fname;
        $scope.lname = sessionStorage.lname;
        
        
    // Request to render wishes on page load
            
        $http({
            method: 'GET',
            url: '/api/users/'+sessionStorage.currentUser+'/wishlist'
            })
            .then(function successCallback(response) {
                var reply = response.data;
                if(reply.data.wishes == []){
                    $scope.wishes = [{title: "Get Adding!", thumbnail: "../static/images/default.jpg", description: "Just click the add button above", url: "https://www.example.com/", added: "Today"}];
                }else {
                    $scope.wishes = reply.data.wishes;
                }

        }, function errorCallback(response) {
            //
        });
        
    // Function to remove a wish to the database     
        $scope.removeWish = function(itemid) {
          // remove wish
          $('#loading').show();
          $http({
                method: 'POST',
                url: '/api/users/'+sessionStorage.currentUser+'/wishlist/'+itemid, 
                data: JSON.stringify({itemid: itemid}),
                headers: {'Content-Type': 'application/json;charset=UTF-8'}
                })
                .then(function (response) {
                    $route.reload();
                    $('#loading').hide();
                    alert(response.data.message);
                });
        };
    });
    
    app.controller('modalctrl', function($scope,$http,$route) {
        var chosen;
        var modal = document.getElementById('modal');
        
    // Displays Modal    
        $("#add").click(function(e){
            e.preventDefault();
            modal.style.display = "block";
        });
        
        
    // Hides the modal when the close button is clicked     
        $(".close").click(function() {
            modal.style.display = "none";
            $scope.title = '';
            $scope.details = '';
            $scope.url = '';
            $scope.image = '';
        });
        
    // Hides the modal when the screen is clicked        
        $(window).on('click', function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            $scope.title = '';
            $scope.details = '';
            $scope.url = '';
            $scope.image = '';
            }
        });
        
    // Stores the selected image from the form    
        $scope.chosenImg = function(index){
            chosen = $scope.options[index];
        };
        
    // Listens for the click on the radion buttons on the form    
        $scope.scrape = function() {
            $('#loading').show();
            $scope.options = [];
            
            if ($('input[name=optionsRadios]:checked', '#form').val() == 'yes') {

                
            //Calls python function to scrape images from the given url.
                $http({
                method: 'POST',
                url: '/api/thumbnails', 

                data: JSON.stringify({url: $scope.url}),
                headers: {'Content-Type': 'application/json;charset=UTF-8'}
                })
                .then(function (response) {
                    for (var i=0; i< response.data.thumbnails.length; i++){
                        
                        $scope.options.push(response.data.thumbnails[i]);
                        
                    }
                    JSON.stringify($scope.options);
                    $('#loading').hide();
                });
            } else {
                // put random image
            }
        };
        
    // Function to add a wish to the database     
        $scope.addWish = function () {
        //Gets details from form
            $('#loading').show();
            var details = {
                title: $scope.title,
                description: $scope.description,
                url: $scope.url,
                image: chosen
            };
            
            $http({
                method: 'POST',
                url: '/api/users/'+sessionStorage.currentUser+'/wishlist',
                data: JSON.stringify(details),
                headers: {'Content-Type': 'application/json'}
                })
                .then(function (response) {
                    $scope.wishes.push({
                        title: $scope.title,
                        description: $scope.description,
                        url: $scope.url,
                        image: $scope.img
                    });
                // Resets form fields
            
                $scope.title = '';
                $scope.description = '';
                $scope.url = '';
                $scope.img = '';
                
                
                
                $('#loading').hide();
                $route.reload()

                alert('Your Wish has been Added');
            }).catch(function(error){
                $('#loading').hide();
                alert(error.data.message);
            });
            
        
            
        };
        
        
        
////////////////////////////////////////////////////////////////////////////        
    
    });
    
    app.controller('sharectrl', function($scope, $http, $route){
        
        var share = document.getElementById('share')
        
    // Displays Share form    
        $("#shareb").click(function(e){
            e.preventDefault();
            share.style.display = "block";
                
        });    

    
    // Hides the share form when the close button is clicked     
        $(".close1").click(function() {
            share.style.display = "none";
            
        });
        
    // Hides the share form when the screen is clicked        
        $(window).on('click', function(event) {
        if (event.target == share) {
            share.style.display = "none";
            
            }
        });
        
            
        $scope.shareWish = function() {
            // Code for adding sharing wish
            $('#loading').show();
            var details = {
                userid: sessionStorage.currentUser,
                firstname: $scope.fname,
                lastname: $scope.lname,
                email: $scope.sendemail
            };
            
            $http({
                method: 'POST',
                url: '/share/',
                data: JSON.stringify(details),
                headers: {'Content-Type': 'application/json'}
                }).then(function(response){
                    $('#loading').hide();
                    $route.reload();
                    alert(response.data.message);
                })
                .catch(function(error){
                    $('#loading').hide();
                    $route.reload();
                    alert(error.data.message);
                })
        };
        
        
        
        $scope.searchWish = function() {
            // Code for adding searching wish
            alert('search function');
        };
    })