Introduction
============
**NOTE: This is early, experimental code.  Use at your own risk and not recommended for production sites.**

collective.chimpdrill makes it easy to send trackable, deliverable, and nicely formatted emails from Plone using Mailchimp (http://www.mailchimp.com) and Mandrill (http://www.mandrill.com).  After installing, there are two new content types: Repository and Template.  Create a Repository, then add Templates inside it.

Configuration
=============
Once installed, you can visit the Mailchimp & Mandrill Settings section of the control panel to enter your Mailchimp API Key and Mandrill API Key.  There is also a field for controlling the Template Schema vocabulary.

Templates
=========
When adding a template, you can either select from an existing template in Mailchimp (vocabulary pulled dynamically from Mailchimp API) or upload a new template.  If you provide an Upload Template Name and Upload Template Code (html), the template will automatically be added to your Mailchimp instance via the API.  

Additional fields on the template allow setting the subject line, the sender, a description, and the Template Data Schema.  The Template Data Schema dropdown determines the schema interface used for the Send form.  Out of the box, there are 4 available schemas: Basic (send to email), Body Only (title, body), Target Only (title, url, targetblock), and Body and Target (title, body, target title, target url, target block).  

The Template Data Schema fields are parsed to build the merge variables and block content for sending an email using the template.  Mandrill respects roughly the same template syntax as Mailchimp.  Thus *|FIRSTNAME|* will be replaced with the merge variable "FIRSTNAME".  In addition to merge variables, you can also fill blocks, defined in the template with the mc:edit attribute on a tag.  For example, <h1 mc:edit="title" /><div mc:edit="body" />, is all the html you need to put into the mail template to be able to use the Body Only schema to populate the blocks.

Next, the template code from the linked template in Mailchimp is run through the Mailchimp inlineCss API method to inline the css for better cross email client rendering.  Then, it will create a template using the inlined code in Mandrill with the name chimpdrill-{MAILCHIMP_TEMPLATE_ID}.

The default view of a template provides two links: Preview and Send.  Preview display the rendered html preview of the template from Mailchimp.  Send presents a form using the Template Data Schema for the Template.  When submitted, an email is sent from Mandrill using the template and merging in all values from the Template Data Schema.

