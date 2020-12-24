import requests, json
from bs4 import BeautifulSoup
import pandas as pd

class NaverMapScraper:
    def __init__(self, query):
        self.API_URL = 'https://map.naver.com/v5/api/search'

        self.graphql_url = 'https://pcmap-api.place.naver.com/place/graphql'

        self.header = {
            'authority': 'pcmap-api.place.naver.com',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
        self.query = query
        
    def scrape_info(self):
        scraped_items = []
        r = self.get_list_info(self.query, 1)
        i = 1
        while True:
            response = self.get_list_info(self.query, i)
            try:
                items = response['result']['place']['list']
                for item in items:
                    data = {
                        'name': item['name'],
                        'category': (',').join(item['category']),
                        'blogReviews': item['reviewCount'],
                        'telephone': item['tel'],
                        'roadAddress': item['roadAddress'],
                        'address': item['address'],
                        'id': item['id']
                    }
                    info = self.get_more_info(data['id'])
                    data['star'] = info['star']
                    data['reviewCount'] = info['review']
                    scraped_items.append(data)
                i = i + 1
            except KeyError:
                break
        # places = pd.DataFrame(data=scraped_items, columns=['name', 'star', 'blogReviews', 'reviewCount', 'category','telephone','roadAddress','address'])
        # df.to_csv('output.csv', encoding='utf-8-sig', index=False)
        return scraped_items
    
    def get_more_info(self, id):
        query = "query getVisitorReviews($input: VisitorReviewsInput, $id: String) {↵  visitorReviews(input: $input) {↵    items {↵      id↵      rating↵      author {↵        id↵        nickname↵        from↵        imageUrl↵        objectId↵        url↵        __typename↵      }↵      body↵      thumbnail↵      media {↵        type↵        thumbnail↵        __typename↵      }↵      tags↵      status↵      visitCount↵      viewCount↵      visited↵      created↵      reply {↵        editUrl↵        body↵        editedBy↵        created↵        replyTitle↵        __typename↵      }↵      originType↵      item {↵        name↵        code↵        options↵        __typename↵      }↵      language↵      highlightOffsets↵      translatedText↵      businessName↵      showBookingItemName↵      showBookingItemOptions↵      bookingItemName↵      bookingItemOptions↵      __typename↵    }↵    starDistribution {↵      score↵      count↵      __typename↵    }↵    hideProductSelectBox↵    total↵    __typename↵  }↵  visitorReviewStats(input: {businessId: $id}) {↵    id↵    name↵    review {↵      avgRating↵      totalCount↵      scores {↵        count↵        score↵        __typename↵      }↵      imageReviewCount↵      __typename↵    }↵    visitorReviewsTotal↵    ratingReviewsTotal↵    __typename↵  }↵  visitorReviewThemes(input: {businessId: $id}) {↵    themeLists {↵      name↵      key↵      __typename↵    }↵    __typename↵  }↵}↵"
        query = query.replace("↵", '\n')
        data = {
            "operationName": "getVisitorReviews",
            "query": query,
            "variables": {
                "id": f"{id}",
                "input": {
                    "bookingBusinessId": None,
                    "businessId": f"{id}",
                    "display": 1,
                    "includeContent": True,
                    "order": None,
                    "page": 1,
                    "theme": "allTypes"
                }
            }
        }
        r = requests.post(self.graphql_url, json=data, headers=self.header).json()
        info = {
            'star': r['data']['visitorReviewStats']['review']['avgRating'],
            'review': r['data']['visitorReviewStats']['visitorReviewsTotal']
        }
        return info

            
    def get_list_info(self, query, page):
        payload= {
            'query': query,
            'caller': 'pcweb',
            'displayCount': 50,
            'page': page,
            'type': 'all',
            'isPlaceRecommendationReplace': 'true',
            'lang': 'ko'
        }
        r = requests.get(self.API_URL, params=payload, headers=self.header).json()
        return r
    
   