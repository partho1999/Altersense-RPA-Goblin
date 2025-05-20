# Variables

'''
# ? Header Tab
    # * Booking Template
    # * Product Type (Products that do not match with portal dropdown)
    # * Construction Type
    
# ? Parties Tab
    # * Delivery Party
     
# ? Details Tab
    # * Summary Marks 
    # * Summary Description 
    # * Cargo Type
    # * Unit
    # * Qty in Pack
    # * Package Type 
    # * HS Code
    # * Country of Origin
'''

settings = {
    'booking' : {
        'header':{
            'booking_template':"H&M",
            'product_type':{
                'vest_top':'Sweatshirt',
                'polo_shirt':'T-Shirt',
                'hoode':'Hoodie',
                't_shirt':'T-Shirt'
            },
            'construction_type':'Knitted'
        },
        'parties':{
            'delivery_party':'H&M HENNES & MAURITZ GBC AB [SEHENNESMAHQ]'
        },
        'details':{
            'summary_marks':{
                
            },
            'summary_desc':{

            },
            'cargo_type':'Flatpack',
            'unit':'PCS',
            'qty_in_pack':50,
            'package_type':'CARTONS',
            'country_of_origin':'BD',
            'hs_code':{
                'country_code' : [
                    {
                        'title': 'ME',
                        'hs_length':8
                    },
                    {
                        'title':'OD',
                        'hs_length':8,
                    }
                ]
            }
        }
    },
    'fcr':{
        'header_tab':{
            'fcr_template':'INCTL EBL'
        },
        'marks&numbers_tab':{
            'modified_description': 'Knitted'
        },
        'parties_tab':{
            'delivery_party':'HM HENNES MAURITZ PTE LTD [SGHENNESMAHQ]'
        }, 
    }
}