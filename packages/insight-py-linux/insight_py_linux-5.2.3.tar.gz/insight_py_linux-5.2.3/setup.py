from setuptools import find_packages
from setuptools import setup

setup(
    name="insight_py_linux",
    author="htsc",
    version="5.2.3",
    author_email="insight@htsc.com",
    description="insight_python_linux",
    long_description="insight_python_linux",
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

              'insight_python/com/libs/linux/python36',
              'insight_python/com/libs/linux/python37',
              'insight_python/com/libs/linux/python38',
              'insight_python/com/libs/linux/python39',
              'insight_python/com/libs/linux/python310',

              ],

    package_dir={
        'insight_python/com/cert': 'insight_python/com/cert',
        'insight_python': 'insight_python',
        'insight_python/com/libs/linux/python36':
            'insight_python/com/libs/linux/python36',
        'insight_python/com/libs/linux/python37':
            'insight_python/com/libs/linux/python37',
        'insight_python/com/libs/linux/python38':
            'insight_python/com/libs/linux/python38',
        'insight_python/com/libs/linux/python39':
            'insight_python/com/libs/linux/python39',
        'insight_python/com/libs/linux/python310':
            'insight_python/com/libs/linux/python310',
    },

    package_data={
        'insight_python/com/cert': ['service-insight_htsc_com_cn_2024.cer', 'InsightClientCert.pem', 'HTISCA.crt',
                                    'InsightClientKeyPkcs8.pem'],
        # 'insight_python': ['requirements.txt'],
        'insight_python/com/libs/linux/python36': ['_mdc_gateway_client.so', 'libmdc_query_client.so',
                                                   'mdc_gateway_client.py',
                                                   'libACE.so.6.4.3', 'libACE_SSL.so.6.4.3', 'libprotobuf.so.11',
                                                   'libcrypto.so.10', 'libssl.so.10'],
        'insight_python/com/libs/linux/python37': ['_mdc_gateway_client.so', 'libmdc_query_client.so',
                                                   'mdc_gateway_client.py',
                                                   'libACE.so.6.4.3', 'libACE_SSL.so.6.4.3', 'libprotobuf.so.11',
                                                   'libcrypto.so.10', 'libssl.so.10'],
        'insight_python/com/libs/linux/python38': ['_mdc_gateway_client.so', 'libmdc_query_client.so',
                                                   'mdc_gateway_client.py',
                                                   'libACE.so.6.4.3', 'libACE_SSL.so.6.4.3', 'libprotobuf.so.11',
                                                   'libcrypto.so.10', 'libssl.so.10'],
        'insight_python/com/libs/linux/python39': ['_mdc_gateway_client.so', 'libmdc_query_client.so',
                                                   'mdc_gateway_client.py',
                                                   'libACE.so.6.4.3', 'libACE_SSL.so.6.4.3', 'libprotobuf.so.11',
                                                   'libcrypto.so.10', 'libssl.so.10'],
        'insight_python/com/libs/linux/python310': ['_mdc_gateway_client.so', 'libmdc_query_client.so',
                                                    'mdc_gateway_client.py',
                                                    'libACE.so.6.4.3', 'libACE_SSL.so.6.4.3', 'libprotobuf.so.11',
                                                    'libcrypto.so.10', 'libssl.so.10'],

    },

    install_requires=[],

    # python_requires='>=3.6.*',
)
