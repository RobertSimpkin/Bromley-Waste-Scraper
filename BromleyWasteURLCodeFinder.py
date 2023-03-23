import mechanize
import re

class BromleyWasteURLCodeFinder:

    def search(postcode: str = None) -> str:
        ''''''

        br = mechanize.Browser()
        br.open('https://recyclingservices.bromley.gov.uk/waste')

        #br.form = list(br.forms())[0]
        br.select_form(nr=0)

        control = br.form.find_control('postcode')

        if postcode is None:
            postcode = input("Please enter your Bromley post code: ")

        control.value = postcode
        br.submit()

        #TODO: Error handling

        br.select_form(nr=0)
        control = br.form.find_control('address')
        items = control.get_items()

        for count, item in enumerate(items[1:-1], start=1): # There are two additional unselectable items in list
            label = item.attrs['label']
            print(f'{count}) {label}')

        user_choice = int(input("Please choose your address (1, 2, 3 etc.): "))

        if 1 <= user_choice <= (len(items) - 2):
            items[user_choice].selected = True
            response = br.submit()
            url = response.geturl()
            url_code = re.findall('\d{7}$', url)[0]
            return url_code
        
        return None
