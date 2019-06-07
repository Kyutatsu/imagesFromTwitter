from django.test import TestCase
import codecs
import datetime
import json
import pickle
from getImagesFromTwitter.views import get_items_from_tweet

# function_in_view


class GeneralTests(TestCase):
    def setUp(self):
        # json.loadsしたtweets_objects. list型にtweetが4つ入っている。
        # tweetのみ、hash-tagあり、単一画像、複数画像が入ってる。
        with open(
                '/Users/kyutatsu/MyProjects/twitterImages/testdata/tweetx4.dump',
                'rb') as file:
            data = pickle.load(file)
        self.tweet_hash_tag = data[0]  # 画像なしなので現段階では使わない
        self.tweet_text_only = data[1]  # 画像なしなので現段階では使わない
        self.tweet_a_photo = data[2]
        self.tweet_3_photos = data[3]

# 画像のないツイートは処理しないので不要だった。    
#    def test_get_items_from_tweet_hash_tag(self):
#        tweet = get_items_from_tweet(self.tweet_hash_tag)
#        dateobj = datetime.datetime(year=2019, month=5, day=23,
#                    hour=0,minute=16,second=33, tzinfo=datetime.timezone.utc)
#        self.assertEqual(tweet['created_at'], dateobj)
#        self.assertEqual(tweet['id_str'], "1131353184021110785")
#        self.assertEqual(tweet['screen_name'], "qtatsu_q")
#        # self.assertEqual(tweet['media_id_str'], None)
#        # self.assertEqual(tweet['media_url_https'], None)
#        self.assertEqual(tweet['text'], 'test\n\n#てすと\n#test')
#        self.assertEqual(tweet['hashtags_text'], ['てすと', 'test'])
#        self.assertEqual(tweet['retweet_count'], 0)
#        self.assertEqual(tweet['favorite_count'], 0)
#        self.assertFalse(tweet['has_multiple_media'])
#        self.assertIs(tweet['label'], None)
#        self.assertIs(tweet['labeler'], None)
#
#    def test_get_items_from_tweet_text_only(self):
#        tweet = get_items_from_tweet(self.tweet_text_only)
#        dateobj = datetime.datetime(year=2019, month=5, day=22,
#                    hour=4,minute=14,second=10, tzinfo=datetime.timezone.utc)
#        self.assertEqual(tweet['created_at'], dateobj)
#        self.assertEqual(tweet['id_str'], "1131050595459010560")
#        self.assertEqual(tweet['screen_name'], "qtatsu_q")
#        # self.assertEqual(tweet['media_id_str'], None)
#        # self.assertEqual(tweet['media_url_https'], None)
#        self.assertEqual(tweet['text'], 'がぞうなし')
#        self.assertEqual(tweet['hashtags_text'], [])
#        self.assertEqual(tweet['retweet_count'], 0)
#        self.assertEqual(tweet['favorite_count'], 0)
#        self.assertFalse(tweet['has_multiple_media'])
#        self.assertIs(tweet['label'], None)
#        self.assertIs(tweet['labeler'], None)

    def test_get_items_from_tweet_a_photo(self):
        tweets = get_items_from_tweet(self.tweet_a_photo)
        dateobj = datetime.datetime(year=2019, month=5, day=22,
                    hour=4,minute=13,second=54, tzinfo=datetime.timezone.utc)
        # ジェネレータを回す
        for idx, tweet in enumerate(tweets):
            self.assertEqual(tweet['created_at'], dateobj)
            self.assertEqual(tweet['id_str'], '1131050527704305664')
            self.assertEqual(tweet['screen_name'], "qtatsu_q")

            self.assertEqual(tweet['media_id_str'], '1131050524088852480')
            self.assertEqual(
                    tweet['media_url_https'],
                    'https://pbs.twimg.com/media/D7JMdYdV4AAuGfj.png'
            )
            btext = codecs.encode('たんたいがぞうてすと https://t.co/N7Zz0M29cf')
            self.assertEqual(tweet['text'], btext)
            self.assertEqual(tweet['hashtags_text'], '[]')
            self.assertEqual(tweet['retweet_count'], 0)
            self.assertEqual(tweet['favorite_count'], 0)
            self.assertFalse(tweet['has_multiple_media'])
            self.assertIs(tweet['label'], None)
            self.assertIs(tweet['labeler'], None)
            self.assertEqual(
                    tweet['tweet_url'],
                    "https://twitter.com/qtatsu_q/status/1131050527704305664"
            )
        self.assertEqual(idx+1, 1)

    def test_get_items_from_tweet_3_photos(self):
        tweets = get_items_from_tweet(self.tweet_3_photos)
        media_obj = [
                ('1131050407684321281','https://pbs.twimg.com/media/D7JMWm0VsAEZhFN.png'),
                ('1131050407692722177','https://pbs.twimg.com/media/D7JMWm2V4AEfGx-.png'),
                ('1131050407675830274','https://pbs.twimg.com/media/D7JMWmyUIAIa7x-.png'),
        ]
        dateobj = datetime.datetime(year=2019, month=5, day=22,
                    hour=4,minute=13,second=26, tzinfo=datetime.timezone.utc)
        # ジェネエータを回す
        for idx, tweet in enumerate(tweets):
            self.assertEqual(tweet['created_at'], dateobj)
            self.assertEqual(tweet['id_str'], '1131050411501035520')
            self.assertEqual(tweet['screen_name'], "qtatsu_q")
            self.assertEqual(tweet['media_id_str'],media_obj[idx][0])
            self.assertEqual(tweet['media_url_https'], media_obj[idx][1])
            btext = codecs.encode('ふくすうがぞうてすと https://t.co/5hlItlr8s8')
            self.assertEqual(tweet['text'], btext)
            self.assertEqual(tweet['hashtags_text'], '[]')
            self.assertEqual(tweet['retweet_count'], 0)
            self.assertEqual(tweet['favorite_count'], 0)
            self.assertTrue(tweet['has_multiple_media'])
            self.assertIs(tweet['label'], None)
            self.assertIs(tweet['labeler'], None)
            self.assertEqual(
                    tweet['tweet_url'],
                    "https://twitter.com/qtatsu_q/status/1131050411501035520"
            )
        self.assertEqual(idx+1, 3)
