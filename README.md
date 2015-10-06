# Jitter - JITT command line interface

JITT is a crowd-sourcing localization service. It holds all your resources along with their translations, and allows your users to suggest better translations or vote on current ones.

JITT will automatically evaluate each user's translation credibility and give each suggested localization a quality score.

At any point you can download the best translations for each resource, and merge them with your current translations (which might have arrived from traditional translation services such as Transifex, Crowsin etc.)

*NOTE: Jitt currently supports Android localization ___only___.
More options are under development*

## How does it work

The process is simple:
- Upload your strings to JITT server. This includes the original text, as well as all current translations.
- Create custom "translation links" for each of your users which will participate in the crowd-sourcing effort. Each link is meant to be used by a single user in a specific locale.
- Send each custom link to the specific user which should have it - You might do so via any delivery mechanism you choose (SMS, Push Message, email, whatever)

*When a user clicks the link, she is sent to a special web-interface showing 5 resources which need to be translated to the user's locale. The user can then, for each of these resources, select a suggested translation or propose a new translation.*

- At any point you may download the results and merge them back to your code base. The best suggested translation for each resource and locale is used for each of your resources.

*A suggested translation score depends on the credibility of the users which voted for it. The credibility of the users is deduced from the quality of the translation they voted for. Both values are continuously calculated in a feedback loop.*

## Translation Flow

1. Log In in http://jitt.io
1. Create a new App and get an API Key and API Secret
1. Download jitter

  `$ pip install jitter`

1. Upload your current original & translated resources to JITT:

  `$ jitter pack --rootdir <path-to-work-tree> | jitter upload <API key> <API secret>`

1. Generate a personalized translation link for one user and one locale:

  `$ jitter link <API key> <API secret> <User Id> <locale>`

  *For example (for otto@lidenbrock.org, Icelandic):*

       $ jitter link 0123456789abcdef fedbca9876543210 otto@lidenbrock.org is

       http://jitt.io/#/start/0123456789abcdef/is/b956ee5099d840cbbc54fddffb180793cf48e77c/otto@lidenbrock.org

  *A few notes regarding links*:

  - You can generate these links programmatically as long as you follow this pattern:

    `http://jitt.io/#/start/<API Key>/<Locale>/<Token>/<UserId>`

  - User Id is an arbitrary string which identifies your users.

  - Token is the SHA1 MAC of the user id using the API Secret.

    Python snippet:

         from hashlib import sha1
         import hmac

         hashed = hmac.new(secret,userid,sha1)
         token = hashed.digest().encode('hex')

    Java snippet:

         SecretKeySpec keySpec = new SecretKeySpec(secret.getBytes(),"HmacSHA1");

         Mac mac = Mac.getInstance("HmacSHA1");
         mac.init(keySpec);
         byte[] result = mac.doFinal(userid.getBytes());
         token = getHexString(result)); // Convert result to hex string by method of your choice

1. Send the links to your users

1. Follow the progress of translation through the JITT.io dashboard, or by using jitter:

         $ jitter status users <API key> <API secret>
         ...
         $ jitter status resources <API key> <API secret>
         ...

   Add `--format csv` to receive the results in a tabular CSV format (default is `json` format)

1. At any point, you can download results and merge them to your work-tree

    `$ jitter download <API key> <API secret> | jitter unpack --rootdir <path-to-work-tree>`

## Preparing your resource files

### General Recommendations

- Make sure all your resources are understandable and easy to translate. For example, avoid using &xxx; directives in your strings as well as too technical content.
- Make sure all your strings are prioritized - this will ensure that the important parts get done as fast as possible
- Make sure all your strings have context - a simple "dialog box X" or "menu Y" can improve your translation quality quite a bit.
- Resources which should not be translated should be marked as non-translateable. Remember that a non-comprehensive string is a real deterrent on users' motivation.
- String arrays can also be translated, but beware - as items in arrays are only referenced by index, don't ever add an item in the middle of an array, or your translations will become skewed.

### Supported Attributes

- ***priority*** - give your resources priority (from 1 to 3). JITT will prioritize translation of highest priority resources.

- ***context*** - each resource has a context string which will be shown to the user. You can add a comment to the XML before a group of resources - its content will be used as context for all resources following (which don't have a specific context attribute).

- ***translatable*** - in order to skip a resource, mark it as `translatable="false"`.

----

Copyright 2015 DoAT. All rights reserved.
