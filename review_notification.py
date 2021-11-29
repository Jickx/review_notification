import requests
import datetime
import json
import yagmail

from tinydb import table, TinyDB


def adding_review(): 
    """Scraping website, collect reviews from it and return json with new negative reviews."""

    url = 'https://shopee.com.my/api/v2/shop/get_ratings?'
    offset = 0
    review_already_exist = False
    new_reviews_list = []
    first_new_review = True

    payload = {
        'filter': '0',
        'limit': '6',
        'offset': '0',
        'shopid': '290952664',
        'type': '0',
        'userid': '290971902'
    }

    db = TinyDB('review_list.json', ensure_ascii=False, encoding='utf-8')
    db.default_table_name = 'review_list'
    first_review_in_db = db.get(doc_id=1)

    while True:
        print(f'--- Page {round(offset/6) + 1} ---')

        payload['offset'] = str(offset)

        r = requests.get(url, payload)    
        data = r.json()

        for number_item in range(6):

            rating_star = data["data"]["items"][number_item]["rating_star"]

            author_username = data["data"]["items"][number_item]["author_username"]
            author_shopid = data["data"]["items"][number_item]["author_shopid"]
            author_shopid_url = f"https://shopee.com.my/shop/{author_shopid}"

            comment = data["data"]["items"][number_item]["comment"]

            images = data["data"]["items"][number_item]["images"]
            images_url = []

            if images is not None:
                for image in images:
                    images_url.append(f"https://cf.shopee.com.my/file/{image}")

            product_name_with_spaces = data["data"]["items"][number_item]["product_items"][0]["name"]

            product_name = product_name_with_spaces.replace(" ", "-")
            shop_id = data["data"]["items"][number_item]["product_items"][0]["shopid"]
            item_id = data["data"]["items"][number_item]["product_items"][0]["itemid"]
            product_url = f"https://shopee.com.my/{product_name}-i.{shop_id}.{item_id}"

            time_in_millis = data["data"]["items"][number_item]["mtime"]

            dt = datetime.datetime.fromtimestamp(time_in_millis)

            dt = dt.strftime("%Y-%m-%d, %H:%M")

            new_review = {'username': author_username, 'author url': author_shopid_url, 'star rating': rating_star, 'rating content': comment, 
                        'images': images_url, 'product name': product_name_with_spaces, 'link to product': product_url, 'date time': dt}

            if first_new_review:
                if not first_review_in_db:
                    print("Creating new db")
                    db.insert({'username': author_username, 'author url': author_shopid_url, 'star rating': rating_star, 'rating content': comment, 
                                'images': images_url, 'product name': product_name_with_spaces, 'link to product': product_url, 'date time': dt})

                    first_new_review = False
                else:
                    db.update(table.Document(new_review, doc_id=1))
                    first_new_review = False            

            if new_review == first_review_in_db:
                print("Item already exist")
                review_already_exist = True
                break

            if rating_star != 5:
                new_reviews_list.append(new_review)

        offset += 6

        if review_already_exist or offset == 120:
            return new_reviews_list

def generate_html():
    """Generate html string from json"""

    html_string = ""
    new_reviews_list_json = json.dumps(adding_review())
    
    list = json.loads(new_reviews_list_json)

    html = ""

    for item in list:
        images_string = ""
        username = item["username"]
        author_url = item["author url"]
        star_rating = int(item["star rating"])
        rating_content = item["rating content"]
        images = item["images"]
        product_name = item["product name"]
        product_url = item["link to product"]
        date = item["date time"]

        username_string = f"<a href=\"{author_url}\">{username}</a>"
        star_string = "&#11088;" * star_rating
        for image in images:
            image_thumbnail = image + "_tn"
            images_string += f"""<a style="width:132px; height:132px; margin-right: 5px;"href=\"{image}\"><img src=\"{image_thumbnail}\" class=\"image\"></a>"""
        product_string = f"<a href=\"{product_url}\">{product_name}</a>"

        html_string += f"""<div style="margin: 10px 50px 10px 50px;"><p style="margin: 10px 0px 0px 0px;">{username_string}</p><p style="margin: 0px 0px;">{star_string}</p><p style="font-size: 1.2em;">{rating_content}</p><p>{images_string}</p><p>{product_string}</p><p style="font-size: 0.8em; color: grey;">{date}</p></div><hr style="margin: 0px 50px;">"""

        html = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body>
            <div style="margin: 50px 0px; margin: 0; padding: 0; border: 0; font-family: Roboto, Helvetica Neue, Helvetica, Arial, 文泉驛正黑, WenQuanYi Zen Hei, Hiragino Sans GB, 儷黑 Pro, LiHei Pro, Heiti TC, 微軟正黑體, Microsoft JhengHei UI, Microsoft JhengHei, sans-serif;">"""
            
        html = html + html_string + "</div></body></html>"

    return html

def sending_email():
    """Get as input html string and send email with it"""

    password = input("Enter your password: ")
    email = input("Enter reciever email: ")
    yag = yagmail.SMTP("shopeereviewnotification@gmail.com", password)
    html_msg = generate_html()

    if html_msg:
        yag.send(email, "Review notification", html_msg)

sending_email()