#  Don't Create Root Collection
## Name
GeoSpatial Root

## Qualified Name
Root::GeoSpatial-Root
## Description
This is the root of the GeoSpatial work

## Category
GeoSpatial

____

# Don't Create Folder
## Name
Digital Products MarketPlace

## Qualified Name
Folder::Digital-Products-MarketPlace
## Description
This is the digital products marketplace.

## Catagory
GeoSpatial

____

#  Don't Create Folder
## Name
GeoSpatial Products

## Qualified Name
Folder::GeoSpatial-Products

## Description
GeoSpatial product offerings.

## Catagory
GeoSpatial
____

#  Don't Create Folder
## Name
Agricultural Products

## Qualified Name
Folder::Agricultural-Products

## Description
Agricultural product offerings.

## Catagory
GeoSpatial
____

#  Don't Create Folder
## Name
Prepared Imagery Products

## Description
Imagry products that are ready for consumption.

## Catagory
GeoSpatial

____

#  Don't Create Folder
## Name
Raw Satellite Imagery Products.

## Qualified Name
Folder::Raw Satellite-Imagery-Products

## Description
Satellite imagery imported from or referenced from external providers.

## Catagory
GeoSpatial

____

# Don't Update Digital Product
## Name
Sentinel-2a

## Qualified Name
DigitalProduct::Sentinel-2a

## Description
Level 2a (surface level) imagery. Updated

## Product Name
Sentinel Level 2A

## Status
Active

## Product Identifier
sentinel-2a

## Maturity
Mature

## Service Life
Until interest and budget wane.

## Category
GeoSpatial

____

#  Don't Create Folder

## Name
Standard Subscription Agreements Folder

## Qualified Name
Folder::Standard-Subscription-Agreements-Folder

## Description
A folder for digital product subscriptions.

## Catagory
GeoSpatial

____
#  Don't Update Digital Subscription
## Name
GeoSpatial Data Products Subscription

# Qualified Name
Subscription::GeoSpatial Data Products Subscription

## Description
A general subscription agreement for GeoSpatial Data Products

## Identifier
GeoSpatial-Sub-0

## Support Level
Best Effort
____

#  Don't Update Agreement
## Name
A test agreement

# Qualified Name
Agreement::A-test-agreement

## Description
A general agreement for testing and testing

## Identifier
Agreement 1

____


	* Agreement Name: `GeoSpatial Data Products Subscription`
	
	* Item Name: `DigitalProduct::Sentinel-2a`
	
	* Agreement Item Id: `Sentinel-2a-Subscription`
	
	* Agreement Start: `2025-08-01`
	
	* Agreement End: `2030-12-31`
	
	* Obligations: `{
  "Attribution": "Required"
}`
	
	* Entitlements: `{
  "Data Download": "Allowed",
  "Data Sharing": "Allowed"
}`
	

#  Don't Link Subscriber->Subscription
##  Subscription
Subscription::GeoSpatial-Data-Products-Subscription

## Subscriber
Agreement::A-test-agreement

___

#  Don't View Data Sharing Agreements
## Output Format
LIST

___

# Don't View Data Sharing Agreements
## Output Format
REPORT
___
# Don't View Report
## Output Format
REPORT
## Output Format Set
Collections


# Provenance

* Results from processing file product.md on 2025-09-01 09:26
