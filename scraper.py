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
                        '업체명': item['name'],
                        '업종': (',').join(item['category']),
                        '블로그리뷰': item['reviewCount'],
                        '전화번호': item['tel'],
                        '도로명': item['roadAddress'],
                        '지번': item['address'],
                        'id': item['id']
                    }
                    info = self.get_more_info(data['id'])
                    data['별점'] = info['star']
                    data['방문뷰'] = info['review']
                    scraped_items.append(data)
                i = i + 1
            except KeyError:
                break
        df = pd.DataFrame(data=scraped_items, columns=['업체명', '별점', '방문뷰', '블로그리뷰', '업종','전화번호','도로명','지번'])
        # df.to_csv('output.csv', encoding='utf-8-sig', index=False)
        return df
    
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
    
    def get_items_info(self, items):
        scraped_items = []
        for item in items:
            data = {
                '업체명': item['name'],
                '업종': (',').join(item['category']),
                '별점': None,
                '리뷰갯수': item['reviewCount'],
                '전화번호': item['tel'],
                '도로명': item['roadAddress'],
                '지번': item['address'],
                '우편번호': None,
                'id': item['id']
            }
        scraped_items.append(data)
        return scraped_items
