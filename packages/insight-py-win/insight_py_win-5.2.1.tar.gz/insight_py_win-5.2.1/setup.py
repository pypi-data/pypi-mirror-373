from setuptools import find_packages
from setuptools import setup

setup(
    name="insight_py_win",
    author="htsc",
    version="5.2.1",
    author_email="insight@htsc.com",
    description="insight_python_win",
    long_description="insight_python_win",
    license='insightpythonsdk',
    project_urls={
        'Documentation': 'https://packaging.python.org/tutorials/distributing-packages/',
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/pypa/sampleproject/',
        'Tracker': 'https://github.com/pypa/sampleproject/issues',
    },

    packages=['insight_python',
              'insight_python/com',
              'insight_python/com/interface',
              'insight_python/com/cert',
              'insight_python/com/insight',

              'insight_python/com/libs/python36',
              'insight_python/com/libs/python37',
              'insight_python/com/libs/python38',
              'insight_python/com/libs/python39',
              'insight_python/com/libs/python310',

              ],

    package_dir={
        'insight_python/com/cert': 'insight_python/com/cert',
        'insight_python': 'insight_python',
        'insight_python/com/libs/python36':
            'insight_python/com/libs/python36',
        'insight_python/com/libs/python37':
            'insight_python/com/libs/python37',
        'insight_python/com/libs/python38':
            'insight_python/com/libs/python38',
        'insight_python/com/libs/python39':
            'insight_python/com/libs/python39',
        'insight_python/com/libs/python310':
            'insight_python/com/libs/python310',
    },

    package_data={
        'insight_python/com/cert': ['service-insight_htsc_com_cn_int_2022.cer', 'InsightClientCert.pem', 'HTISCA.crt',
                                    'InsightClientKeyPkcs8.pem'],
        # 'insight_python': ['requirements.txt'],
        'insight_python/com/libs/python36': ['_mdc_gateway_client.pyd', 'ACE.dll', 'ACE_SSL.dll', 'libeay32.dll',
                                             "ssleay32.dll", "insight_query_client.dll", "mdc_gateway_client.py"],
        'insight_python/com/libs/python37': ['_mdc_gateway_client.pyd', 'ACE.dll', 'ACE_SSL.dll', 'libeay32.dll',
                                             "ssleay32.dll", "insight_query_client.dll", "mdc_gateway_client.py"],
        'insight_python/com/libs/python38': ['_mdc_gateway_client.pyd', 'ACE.dll', 'ACE_SSL.dll', 'libeay32.dll',
                                             "ssleay32.dll", "insight_query_client.dll", "mdc_gateway_client.py"],
        'insight_python/com/libs/python39': ['_mdc_gateway_client.pyd', 'ACE.dll', 'ACE_SSL.dll', 'libeay32.dll',
                                             "ssleay32.dll", "insight_query_client.dll", "mdc_gateway_client.py"],
        'insight_python/com/libs/python310': ['_mdc_gateway_client.pyd', 'ACE.dll', 'ACE_SSL.dll', 'libeay32.dll',
                                              "ssleay32.dll", "insight_query_client.dll", "mdc_gateway_client.py"],

    },

    install_requires=[],

    # python_requires='>=3.6.*',
)
