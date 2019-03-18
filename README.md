# Safari Samesite cookies issue (Webkit Bug 188165)

Safari 12 on iOS and Mac OS X doesn't send cookies nor allow JS to read cookies set on response if the request is made by a cross-site redirection. [At bugs.webkit.org, this issue is marked as RESOLVED](https://bugs.webkit.org/show_bug.cgi?id=188165), but it breaks for the current version of Safari 12 (as of March 18, 2019). This Django 2.1 app reproduces this problem consistently. A [ticket](https://code.djangoproject.com/ticket/30250) has also been created on Django to suggest a default of no samesite for both CSRF and Session cookies.

## Steps to Reproduce

Tested on:

* Mac Mojave 10.14.3 (18D109), Safari 12.0.3 (14606.4.5)
* iOS 12 12.1.4

---

0. Install requirements:

        pip install -r requirements.txt

1. Run local server:
        
        python manage.py runserver

2. Add lines below to your `/etc/hosts` to support the subdomain `aaa` on localhost:

        127.0.0.1   aaa.localhost
        ::1         aaa.localhost

3. On Safari 12, open `http://localhost:8000/target/`. You should see something like:

        request.session.session_key: None 
        request.session['obj']: a916f354195a4a45b6933ef41b26bdda 

        request.META['CSRF_COOKIE']: 
        CSRF cookie (from JS): NHaGQEiZ0PofLDqOG0vgYi7mD4kpBFvcEsxRQdLssjpaxG6hKixjT8iKaIOAau2g 

4. Refresh page. Now you'll see `request.session.session_key` and `request.META['CSRF_COOKIE']` filled. Will also see `request.META['CSRF_COOKIE']` and `CSRF cookie (from JS)` values are the same. If you click "submit", you'll see an alert with `success`. That's the expected behavior. If you look into Safari developer tools > Storage > Safari developer tools, you'll see something like:

        csrftoken   NHaGQEiZ0PofLDqOG0vgYi7mD4kpBFvcEsxRQdLssjpaxG6hKixjT8iKaIOAau2g    localhost   /   3/16/2020, 6:33:01 PM   73 B            Lax
        sessionid   6yga6jg6zhfkpnnwtxsdxcdi3gf4j72s    localhost   /   4/1/2019, 6:33:01 PM    41 B        ✓   Lax

   Note the value `Lax` for Same-Site. That's what causes the issue on Safari. Let's break it...

4. Go to `http://aaa.localhost:8000/redirect/`, you'll be redirected to `http://localhost:8000/target/`, and you'll see this:

        request.session.session_key: None 
        request.session['obj']: 478b57a0d9b14da6ba55602f0f70422d 

        request.META['CSRF_COOKIE']: 
        CSRF cookie (from JS): null 

   **That's the issue. Safari didn't send any cookies for the GET triggered by the cross-site redirection.** That's why `session_key` for `request` is None and `request.META['CSRF_COOKIE']` is empty.
   Also, if you click "submit" you'll see a `error 403` due to CSRF protection, because the JS code cannot read the cookie set by the response of the GET.

   A cookie with Same-site `Lax` should allow the browser to send it on the request and read it on the response, even if the request is made by a cross-site redirection. But neither is possible on Safari with `Lax`. Other browsers don't behave that way. On Chrome, if you try this same flow, you'll see the same values you saw when you did a GET to `http://localhost:8000/target/`.

5. Django-specific problem: after `http://aaa.localhost:8000/redirect/`, the browser makes a GET to `http://localhost:8000/target/` without `request.META['CSRF_COOKIE']`. This causes Django's `get_token` to call `_get_new_csrf_string` and set a new CSRF cookie on the response. That breaks POST interactions on other open tabs. Again, that doesn't happen on other browsers.

## Solution?

Update `settings.py` to:

        CSRF_COOKIE_SAMESITE = None
        SESSION_COOKIE_SAMESITE = None
