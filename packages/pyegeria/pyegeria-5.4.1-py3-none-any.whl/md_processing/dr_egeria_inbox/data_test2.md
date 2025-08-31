
___


# foo Update Glossary
## Glossary Name
Test Glossary
## Description
This glossary is just for testing

___

# foo Update Term
## In Glossary
Test Glossary
## Term Name
Hospital Identifier
## Description
Identifies each hospital uniquely. Used within the PatientId field.

___

# foo Update Data Dictionary
## Name
Clinical Trial Data Dictionary

## Description
A data dictionary for clinical trial data elements.


# foo Update Data Dictionary
## Name
Pharma Data Dictionary

## Description
A data dictionary of elements relevant to the Pharma communities.


___

# foo Update Data Spec

## Data Specification 

Data Specification for the Teddy Bear Dropt Clinical Trial

## Description
Principle data requirements for Teddy Bear Dropt Clinical Trial. Meow

## Qualified Name
DataSpec::Data Specification for the Teddy Bear Dropt Clinical Trial

## Classifications

## Guid


___


# foo Update Data Specification

## Data Specification Name 

Test Spec2

## Description
A test spec - Meow

## Qualified Name

## Classifications

## Guid

## Additional Properties
{
    "a prop" : "meow",
    "another" : "woof"
}
___

# foo Update Data Dictionary

## Dictionary Name 

dw

## Description
A data dictionary for dan..
## Qualified Name
DataDict::dw

## Classifications

## GUID


___


# foo Update Data Structure

## Data Structure Name 

TBDF-Incoming Weekly Measurement Data

## Description
This describes the weekly measurement data for each patient for the Teddy Bear dropt clinical trial. 

## Qualified Name
DataStruct::TBDF-Incoming Weekly Measurement Data

## Namespace

## In Data Specification
Data Specification for the Teddy Bear Dropt Clinical Trial

## Version Identifier


## Guid


___

# foo Update Data Structure

## Data Structure Name 

WWT-Incoming Weekly Measurement Data

## Description
A collection of data fields that form a data structure.

## Qualified Name
DataStruct::WWT-Incoming Weekly Measurement Data

## In Data Specification
Test Spec2

## Namespace


## Version Identifier


## GUID



___

# Foo Update Data Field

## Data Field Name 

PatientId

## Description
Unique identifier of the patient

## Qualified Name
DataField::PatientId


## Data Type

String

## Guid

## Data Class

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary, Pharma Data Dictionary

## In Data Structure
TBDF-Incoming Weekly Measurement Data
DataStruct::WWT-Incoming Weekly Measurement Data

## Glossary Term
GlossaryTerm::ClinicalTrialTerminology::PatientId
___



# Foo Update Data Field

## Data Field Name

HospitalId

## Description
Unique identifier for a hospital. Used in forming PatientId.

## Qualified Name
DataField::HospitalId

## Data Type
String

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary

## In Data Structure

DataStruct::TBDF-Incoming Weekly Measurement Data
DataStruct::WWT-Incoming Weekly Measurement Data

## Position
1

## Min Cardinality
0

## Max Cardinality
1

## Glossary Term
Term::Hospital Identifier

## Parent Data Field
DataField::PatientId

## Journal Entry
Just creating this term

___

# Foo Update Data Field

## Data Field Name 

PatientSN

## Description
Unique identifier of the patient within a hospital.

## Qualified Name
DataField::PatientSN


## Data Type

String
## Position
2

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary

## In Data Structure
DataStruct::TBDF-Incoming Weekly Measurement Data
DataStruct::WWT-Incoming Weekly Measurement Data

## Parent Data Field
DataField::PatientId

## Journal Entry
Just creating this term

___

#  foo Update Data Class

## Data Class Name 

Date

## Description
A date of the form YYYY-MM-DD -moo

## Qualified Name
DataClass::Date

## Data Type
date
## Position
0

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary


## Containing Data Class

## Specializes Data Class

## Journal Entry
Just creating this date



___

#  Update Data Class

## Data Class Name 

ISO-Date

## Description
ISO 8601 standard date. A date of the form YYYY-MM-DD

## Qualified Name
DataClass::ISO-Date

## Data Type
date
## Position
0

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary



## Containing Data Class
DataClass::Address

## Specializes Data Class

>DataClass::Date

## Journal Entry
Just creating this date


___


# Foo Update Data Field

## Data Field 

Date

## Description
A date of the form YYYY-MM-DD

## Qualified Name
DataField::Date


## Data Type
date

## Position
0

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary

## In Data Structure
TBDF-Incoming Weekly Measurement Data,
DataStruct::WWT-Incoming Weekly Measurement Data

## Parent Data Field

## Data Class
DataClass::ISO-Date

## Journal Entry
Just creating this date


___



#  Foo Update Data Class

## Data Class Name 

Address

## Description
Address Class

## Qualified Name



## Data Type

String
## Position
0

## Min Cardinality
0

## Max Cardinality
1

## In Data Dictionary
DataDict::Clinical Trial Data Dictionary


## Containing Data Class

## Specializes Data Class

## Journal Entry
Just creating this date
