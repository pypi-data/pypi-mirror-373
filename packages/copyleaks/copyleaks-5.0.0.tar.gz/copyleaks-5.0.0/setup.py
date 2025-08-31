from distutils.core import setup
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='copyleaks',
    packages=['copyleaks', 'copyleaks.exceptions', 'copyleaks.models', 'copyleaks.models.submit', 'copyleaks.models.submit.properties', 'copyleaks.clients', 'copyleaks.helpers','copyleaks.models.submit.Webhooks.HelperModels.ResultsModels','copyleaks.models.submit.Webhooks.HelperModels.NotificationsModels','copyleaks.models.submit.Webhooks.HelperModels.NewResultModels','copyleaks.models.submit.Webhooks.HelperModels.ExportModels','copyleaks.models.submit.Webhooks.HelperModels.ErrorModels','copyleaks.models.submit.Webhooks.HelperModels.CompletedModels','copyleaks.models.submit.Webhooks.HelperModels.BaseModels','copyleaks.models.submit.Webhooks.HelperModels','copyleaks.models.submit.Webhooks','copyleaks.models.TextModeration.Responses','copyleaks.models.TextModeration.Responses.Submodules','copyleaks.models.TextModeration.Requests','copyleaks.models.constants'
 ],
    version='5.0.0',
    description='Copyleaks API gives you access to a variety of plagiarism detection technologies to protect your online content. Get the most comprehensive plagiarism report for your content that is easy to use and integrate.',
    author='Copyleaks ltd',
    author_email='sales@copyleaks.com',
    url='https://api.copyleaks.com',
    download_url='https://github.com/Copyleaks/Python-Plagiarism-Checker',
    keywords=['copyleaks', 'api', 'plagiarism', 'content', 'checker', 'online', 'academic', 'publishers', 'websites'],
    install_requires=[
        'requests', 'python-dateutil', 'pytz','pydantic'
    ],
    classifiers=[],
	long_description=long_description,
	long_description_content_type='text/markdown',
)
