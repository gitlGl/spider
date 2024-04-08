# -*- coding: utf-8 -*-
LOG_LEVEL = 'ERROR'
BOT_NAME = 'spider'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

ROBOTSTXT_OBEY = False

HTTPERROR_ALLOW_ALL = True

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
}

CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY = 1

DOWNLOAD_TIMEOUT = 15  # 设置超时时间为15秒
RETRY_ENABLED = False



ITEM_PIPELINES = {
    'pipelines.PonyPipeline': 300,
}
