## MetaHCR - Metagenomics on Hydrocarbon Resources

MetaHCR is a web application interface to a relational
database that stores the inter-relationships amongst
Hydrocarbon Resource Samples, their Single Gene and
Metagenome Analyses and the Organisms found via these
analyses. Ancillary tables provide metadata.

MetaHCR consists of a PostgreSQL database and a Django (verson 1.7) application. The database
has data on the following:
1. 33 Investigations
2. 305 Samples
3. 492 Biological Analyses - 482 Single Gene and 10 Metagenome
4. 45,906 Organisms

## Documentation
* [Users Guide](https://github.com/metahcr/metahcr_v1/blob/master/docs/MetaHCRUsersGuide-v1.0.pdf)
* [Administrators Guide](https://github.com/metahcr/metahcr_v1/blob/master/docs/MetaHCRAdminGuide-v1.0.pdf)
* [Data Descriptions](https://github.com/metahcr/metahcr_v1/blob/master/docs/MetaHCRData-v1.0.pdf)
* [Database Schema Diagrams](https://github.com/metahcr/metahcr_v1/blob/master/docs/schemas/index.html)

## Installation
First, using git or the GitHub facilities, download this repository. The
following paragraphs show the easiest and most straight-forward way to
install the database and to install and run MetaHCR. Other types of
installations - such as using the Apache web server - are more involved.
It is suggested that you consult the Django [documentation](https://docs.djangoproject.com/en/1.7/howto/deployment/).

### Database Installation
MetaHCR was developed using PostgreSQL version 9.2 It most likely will work
with newer versions. If you do not have PostgreSQL installed on your system,
visit the [PostgreSQL website](https://www.postgresql.org/download/).
#### Build the Database

The database file located in the data directory. Note that is approximately 52 MB in size and it is handled with [git LFS](https://git-lfs.github.com/). It is a PostgreSQL
dump file that can be used by the pg_restore PostgreSQL utility. Prior to
restoring the database, you will need to create a user and a database. NB: You can
use the pgadmin tool to accomplish all of these tasks as well as the restoration
of the database. The command line version is shown below:

Have available a user with super user privileges - the user postgres is
used in the examples. You need to have this user's password. You will be prompted for a password for the new user and the super user.

Create a new user:

`$ createuser -U postgres -P -s -e metahcradmin`

Create a new - empty - database:

`$ createdb -U metahcradmin metahcr_public_v34`

Restore the database using the following command:

`$ pg_restore -U metahcradmin -d metahcr_public_v34 2017-08-16-metahcr_public_v34.backup`

#### Adjust Django settings.py file
You must modify the Django settings.py file to reflect the password
that you have chosen for the metahcradmin user. The file is located [here](https://github.com/metahcr/metahcr_v1/blob/master/metahcr/metahcr/settings.py).
Change the PASSWORD value in the DATABASES variable to metahcradmin's password. Save the settings.py file.

#### Install Python
Python may already be installed on your system. At the command line type:

`$ python`

If the version is less than 2.7.9, you must install a newer 2.7 version. *Note:
do not use any Python version 3.x.*
#### Install Django and Python Libraries
In addition to Django, MetaHCR uses other Python libraries; these need
to be installed. To install them you will use the pip utility that comes
with Python. The pip utility that was installed may need to be updated.
Documentation for pip is available [here](https://pip.pypa.io/en/stable/)

The next steps use the pip utility to load all required Python libraries
including Django:

Locate the requirements.txt file that came with the MetaHCR distribution.
It can be found in the top level directory: metahcr_v1. It is a list of
all the libraries (including Django) that need to be installed.
Open a command line and change to the directory where the requirements.txt is located.
Type the following:

`$ pip install -r requirements.txt`

*Note that on Windows systems, you might need to install the Microsoft
Visual C++ Compiler for Python 2.7 which can be found
[here](https://www.microsoft.com/en-us/download/details.aspx?id=44266).*

The pip install command should download and install (and in some cases build)
all the required Python libraries and Django. Note that some of the
libraries are large, so this installation may take several minutes.

#### Start the Django Application
The easiest and most straight-forward way of starting the MetaHCR application
is to use Django's built-in web server. **Note this server should never be
used in a production environment.**

Change directory:

`$ cd metahcr_v1/metahcr`

Run the Django web server:

`$ python manage.py runserver`

The MetaHCR application can now be accessed by opening a browser (Chrome
is preferred but other modern browsers should work) and entering the
following URL: <http://localhost:8000> or <http://127.0.0.1:8000>. The MetaHCR
home page should appear. You must log in to use MetaHCR.

#### Log In
The project's initial database has a user account that you can use to log in to
the MetaHCR application. The name/password is guest/guest.
