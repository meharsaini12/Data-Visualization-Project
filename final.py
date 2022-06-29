"""Uses COVID-19 information and provides vaccine eligibility, vaccine sites, 
and data visualization of vaccine information. """

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from haversine import haversine
from vincenty import vincenty
import sys
import combined

class Eligibility:
    """Takes in a file and uses the information from the file to tell each 
    individual part of the file the phase in which they will receive the 
    vaccine. 
    
    Attributes:
        file (filepath): The filepath in which the file is open and parsed.
        
        info(dict): A dictionary of information in the file. This consists of 
        the individuals name, age, immunocompromised status, vaccine status
        job and zipcode. """
        
    def __init__(self, file):
        """Takes in file and puts all of the information in a dictionary. 
        
        Attributes: 
            See attributes defined for class. """
            
        self.info = {}
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                line_data = line.split()
                name = line_data[0]
                age = int(line_data[1])
                immunocompromised = line_data[2]
                job = line_data[3]
                preference = line_data[4]
                zipcode = line_data[5]
                phase = self.eligible(age, immunocompromised, job)
                self.info[name] = (name, age, immunocompromised, job, preference, zipcode, phase)
                
    def eligible(self, age, immunocompromised, job):
        """Determines which phase the individual on each line of the file is
        eligible for to take the vaccine based on age, immunocompromised 
        status, job. 
        
        Args: 
            age(int): The age of the individual. 
            
            immunocompromised (str): Whether or not the individual is
            immunocompromised. 
            
            job (str): The profession of the individual. 
            
        Returns: 
            str: Outputs the phase in which each individual is eligible for the
            COVID-19 vaccine. """
            
        phase1_jobs = ["doctor", "nurse", "therapist"]
        phase2_jobs = ["cashier", "teacher"]
        if age >= 60 or job in phase1_jobs:
            return "phase 1"
        elif immunocompromised == "yes" or job in phase2_jobs:
            return "phase 2"
        else:
            return  "phase 3"
            
    def __repr__(self):
        """Formal represenation of the class Eligibility. 
        
        Returns: 
            str: Returns the formal representation of the individual and the 
            phase they are eligible for. """
        
        string = ""
        for name in self.info:
            person = self.info[name]
            string += name + " " + str(person[6]) + "\n"
        return string
    
class Zipcode:
    """Ask the user to input a zipcode and return a list of vaccine clinics 
    in latitude and longitude.
    
    Attributes: 
        zipcodes (dict of str): Dictionary of zipcodes and their latitude and 
        longitude. 
        
        vaccine_locations (dict of str): Dictionary of zipcodes and their 
        latitude and longitude of the vaccine sites. 
    
    Returns: 
        Dict of floats: Appended dictionary of longitudes and latitudes.  
    
    Sources:
        Hurst, E. (n.d.). All US zip codes with their corresponding latitude and longitude coordinates. 
        Comma delimited for your database goodness. Source: http://www.census.gov/geo/maps-data/data/gazetteer.html. 
        GitHub. Retrieved December 15, 2021, from https://gist.github.com/erichurst/7882666"""
    
    def __init__(self, file1, file2):
        """Parses through two different files to obtain information about the 
        location of the vaccine as well as zipcode information about the
        individual. 
        
        Attributes: 
            See attributes for the class. 
            
        Args: 
            file1 (str): File containing zipcodes of individuals. 
            
            file2 (str): File containing zipcode and location information
            about vaccine locations. """
            
        self.zipcodes = { }
        self.vaccine_locations = { }
        with open(file1, "r", encoding="utf-8") as f:
            for i in f: 
                zipdict = { }
                zip, lat, lng= i.split(",")
                zipdict["zip"] = zip.strip()
                zipdict["lat"] = float(lat.strip())
                zipdict["lng"] = float(lng.strip())
                self.zipcodes[zip] = zipdict
        with open(file2, "r", encoding = "utf-8") as f:
            for i in f:
                location_dict = { }
                name, zip, lat, lng = i.split(",")
                location_dict["name"] = name.strip()
                location_dict["zip"] = zip.strip()
                location_dict["lat"] = float(lat.strip())
                location_dict["lng"] = float(lng.strip())
                self.vaccine_locations[name] = location_dict

    def get_latlng(self, zipcode):
        """Retrieves the latitude and longitude of the zipcode specified. 
        
        Args: 
            zipcode (str): The zipcode of the individual. 
            
        Returns: 
            tuple (str): Returns a tuple of strings, that has that latitude and 
            longitude of the zipcode. """
            
        zip = self.zipcodes[zipcode]
        return (zip["lat"], zip["lng"])

    def nearest(self, p1):
        """Compares the latitude and longitude of the individual's zipcode to 
        vaccine locations and retrieves the closest location. 
        
        Args: 
            p1 (float): latitude and longitude of the individual's zipcode. 
            
        Returns: 
            nearest_name (str): Returns the name of the nearest vaccine 
            location. """
            
        nearest_distance = sys.float_info.max
        nearest_name = ""
        for name in self.vaccine_locations:
            location = self.vaccine_locations[name]
            p2 = (location["lat"], location["lng"])
            distance = self.get_dist(p1, p2)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_name = name
        return nearest_name


    def get_dist(self, p1, p2, miles=False):
        """Calculate the distance between two latitude/longitude coordinates.
        
        Args:
            p1 (float): latitude and longitude of one location.
            p2 (float): latitude and longitude of second location.
            miles (bool): if True, return result in terms of miles
        
        Returns:
            float: the distance between p1 and p2"""
        dist = vincenty(p1, p2, miles=miles)
        if not dist:
            dist = haversine(p1, p2, unit='mi' if miles else 'km')
        return dist

def main():
    """Creates an instance of the Zipcode and Eligibility classes and uses them
    to methods to find the nearest location. 
    
    Side effects: 
        Prints the nearest zipcode location to the individual's zipcode. 
        Prints name not found if the user input's a name that is not given in 
        a list. """
    zipcode = Zipcode("zipcodes.txt","vaccine_locations.txt")
    eligibility = combined.Eligibility("fariba.txt")
    name = input("What is your name? ")
    if name in eligibility.info:
        person = eligibility.info[name]
        person_zipcode = person[5]
        p1 = zipcode.get_latlng(person_zipcode)
        nearest_location = zipcode.nearest(p1)
        print (nearest_location)
    else:
        print("Name not found")


if __name__ == "__main__":
    main()

def main():
    """Creates instance of Eligibility class to be able to use it's methods. 
    
    Side effects: 
        Prints the instance of the Eligibility class. """
        
    eligibility = Eligibility("fariba.txt")
    print(eligibility)


def graphyes(file):
    """Uses the file to provide a graph that indicates how many individual 
    would take the vaccine. 
    
    Args: 
        file (str): A file that contains information about the individuals. 
        
    Returns:
        A graph that indicates individuals who are willing to get the vaccine 
        compared to their ages. 
    
    Sources: 
    https://pandas.pydata.org/docs/reference/api/pandas.cut.html: line 242,
    Allowed me to use the cut method of the pandas. This would allow for there 
    to be separation of ages in bins on the x-axis. 
    
    https://www.geeksforgeeks.org/plotting-multiple-bar-charts-using-matplotlib
    -in-python/ : lines 240-244, allowed me to develop the code for 
    production of two bars for each x-axis label, using two sets of data. 
    
    https://datatofish.com/bar-chart-python-matplotlib/ : lines 245-248, allowed
    me to learn about the different methods you can use from the plt class to 
    edit the bar graph.
    
    https://www.easytweaks.com/pandas-read-text-files/. 
    This source taught me how to take information from a text file and create a dataframe using that information"""
        
    df = pd.read_csv(file, delimiter =' ', names =['name', 'age', 'immunocompromised', 'job', 'will take vaccine?', 'zipcode'], index_col = False)
    dfyes = df[df["age"] < 1000][df["will take vaccine?"] == 'yes'][["will take vaccine?", "age"]]
    dfyes["Age Group"] = pd.cut(x=df['age'], bins = [0, 25, 50, 75, 100], labels = ["18-24", "25-44", "45-64", "65-80"])
    immuno = dfyes.groupby("Age Group")['will take vaccine?'].count()
    graph = immuno.plot.bar(x = "Age Group", y = 'will take vaccine?')
    plt.title("Individuals Who Would Take The Vaccine")
    plt.xlabel("Age Groups")
    plt.ylabel("Number of People")
    final = plt.show()
    return final

def graphno(file):
    """Uses the file to provide a graph that indicates how many individual 
    would not take the vaccine. 
    
    Args: 
        file (str): A file that contains information about the individuals. 
        
    Returns:
        A graph that indicates individuals who are not willing to get the 
        vaccine compared to their ages.
        
    Sources: 
    https://pandas.pydata.org/docs/reference/api/pandas.cut.html: line 277,
    Allowed me to use the cut method of the pandas. This would allow for there 
    to be separation of ages in bins on the x-axis. 
    
    https://www.geeksforgeeks.org/plotting-multiple-bar-charts-using-matplotlib
    -in-python/ : lines 279-282, allowed me to develop the code for 
    production of two bars for each x-axis label, using two sets of data. 
    
    https://datatofish.com/bar-chart-python-matplotlib/ : lines 279-282, allowed
    me to learn about the different methods you can use from the plt class to 
    edit the bar graph.
    
    https://www.easytweaks.com/pandas-read-text-files/. 
    This source taught me how to take information from a text file and create a dataframe using that information
"""
         
    df = pd.read_csv(file, delimiter =' ', names =['name', 'age', 'immunocompromised', 'job', 'will take vaccine?', 'zipcode'], index_col = False)
    dfno = df[df["age"] < 1000][df["will take vaccine?"] == 'no'][["will take vaccine?", "age"]]
    dfno["Age Group"] = pd.cut(x=df['age'], bins = [0, 25, 50, 75, 100], labels = ["18-24", "25-44", "45-64", "65-80"])
    immuno = dfno.groupby("Age Group")['will take vaccine?'].count()
    graph = immuno.plot.bar(x = "Age Group", y = 'will take vaccine?')
    plt.title("Individuals Who Would Not Take The Vaccine")
    plt.xlabel("Age Groups")
    plt.ylabel("Number of People")
    final = plt.show()
    return final

graph1 = graphyes("fariba.txt")
graph2 = graphno("fariba.txt")
print(graph1)   
print(graph2)