# Safari Samesite cookies issue (Webkit Bug 188165)

Safari 12 on iOS and Mac OS X doesn't send cookies nor allow JS to read cookies set on response if the request is made by a cross-site redirection. As of March 13, 2019, [this issue is still open](https://bugs.webkit.org/show_bug.cgi?id=188165). This Django 2.1 app reproduces this problem consistently.

## Steps to Reproduce

Tested on Mac Mojave `10.14.3 (18D109)`, Safari 12 user-agent `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15`. Expect same to happen on Safari 12 on iOS `12.1.4`.

0. Install requirements:

        pip install -r requirements.txt

1. Run local server:
        
        python manage.py runserver

2. Add lines below to your `/etc/hosts` to support the subdomain `aaa` on localhost:

        127.0.0.1   aaa.localhost
        ::1         aaa.localhost

3. On Safari 12, open `http://localhost:8000/target/`. You should see `request.META['CSRF_COOKIE']` empty and `CSRF cookie (from JS):` filled. If you click "submit", you'll see an alert with `success`.

4. Refresh page. Now both values will be the same. That's the expected behavior. If you look into Safari developer tools > Storage > Safari developer tools, you'll see something like:

        csrftoken   YD8UeC1U5xdN29O43CCikrMUS0BIEGRbl5Aecgko35wymJYEdCWGZh7HJume7QOJ    localhost   /   3/11/2020, 4:05:57 PM   73 B            Lax

   Note the value `Lax` for Same-Site. That's what causes the issue on Safari. Let's break it...

4. Go to `http://aaa.localhost:8000/redirect/`, you'll be redirected to `http://localhost:8000/target/`, and you'll see this:

        request.META['CSRF_COOKIE']: 
        CSRF cookie (from JS): null 

   Also, if you click "submit" you'll see a `error 403` due to CSRF protection, because the JS code couldn't read the cookie set by the response of the GET that rendered the page.

5. **That's wrong!** A cookie with Same-site `Lax` should allow the browser to send it on the request and read it on the response, even if the request is made by a cross-site redirection. But neither is possible on Safari with `Lax`. Other browsers don't behave that way, e.g., on Chrome, if you try this same flow, you'll see both `request.META['CSRF_COOKIE']` and `CSRF cookie (from JS)` filled on 

6. Django-specific problem: after `http://aaa.localhost:8000/redirect/`, the browser makes a GET to `http://localhost:8000/target/` without `request.META['CSRF_COOKIE']`. This causes Django's `get_token` to call `_get_new_csrf_string` and set a new CSRF cookie on the response. That breaks POST interactions on other open tabs. Again, that doesn't happen on other browsers.

## Solution?

Update `settings.py` to:

        CSRF_COOKIE_SAMESITE = None
        SESSION_COOKIE_SAMESITE = None
