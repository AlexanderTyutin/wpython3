#!/usr/bin/python3
import urllib.request
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
from xmlrpc import client
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts

class WPublisher:
	def __init__(self, inWpUrl, inWpUserName, inWpPassword, debug):
		self.wpUrl = inWpUrl;
		self.wpUser = inWpUserName;
		self.wpPass = inWpPassword;
		self.wpClient = None;
		try:
			self.wpClient = Client(self.wpUrl, self.wpUser, self.wpPass);
		except:
			print("Error while connecting to XMLRPC:");
			return None;
		if (debug):
			print("Successfully connected to XMLRPC.php");
		
	def post_article(self, articleTitle, articleCategories, articleContent, articleTags, imageUrl, tempDir, imageName, dirDelimiter, postStatus):
		# ---	Get image extension
		imgExt = imageUrl.split('.')[-1].lower();
		# --------------------------------------------------------------
		self.imgPath = tempDir + dirDelimiter + imageName + "." + imgExt;
		self.articleImageUrl = imageUrl;
		# ---	Download image file
		f = open(self.imgPath,'wb');
		try:
			f.write(urllib.request.urlopen(self.articleImageUrl).read());
		except:
			print("Error downloading image");
			return -1;
		f.close()
		# --------------------------------------------------------------
		# ---	Upload image to WordPress
		filename = self.imgPath;
		# prepare metadata
		data = {'name': imageName+'.'+imgExt,'type': 'image/'+imgExt,};
		# read the binary file and let the XMLRPC library encode it into base64
		try:
			with open(filename, 'rb') as img:
				data['bits'] = xmlrpc_client.Binary(img.read());
		except:
			print("Error while reading downloaded image file");
			return -2;
		try:
			response = self.wpClient.call(media.UploadFile(data));
		except:
			print("Error while uploading image file");
			return -3;
		attachment_id = response['id'];
		# --------------------------------------------------------------
		# ---	Post article
		post = WordPressPost();
		post.title = articleTitle;
		post.content = articleContent;
		post.terms_names = { 'post_tag': articleTags,'category': articleCategories};
		# More about post statuses: https://python-wordpress-xmlrpc.readthedocs.io/en/latest/ref/methods.html#wordpress_xmlrpc.methods.posts.GetPostStatusList
		post.post_status = postStatus;
		post.thumbnail = attachment_id;
		try:
			post.id = self.wpClient.call(posts.NewPost(post));
		except:
			print("Error while posting article");
			return -4;
		print('Post Successfully posted. Its Id is: ',post.id);
		# --------------------------------------------------------------
		return post.id;
		
if __name__ == "__main__":
	# Usage example
	wp = WPublisher('https://YOUR_SITE_NAME/xmlrpc.php', 'YOUR_SITE_USER', 'YOUR_SITE_USER_PASSWORD', debug=True);
	wp.post_article('Test 001', ['test', 'classes'],
					'Test content', ['remote', 'post'],
					'https://www.python.org/static/img/python-logo.png',
					'/tmp/', 'pic001', '/', 'publish');
