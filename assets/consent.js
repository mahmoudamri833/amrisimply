/* amrisimply — mesure d'audience avec consentement prealable (RGPD).
   Mode strict : AUCUN script Google n'est charge et AUCUN cookie n'est
   depose tant que le visiteur n'a pas clique « D'accord ». Un refus est
   retenu et rien ne se charge. Le choix expire apres 180 jours, puis la
   question est reposee. Le signal Global Privacy Control vaut refus,
   sans afficher la banniere. */
(function () {
  'use strict';
  var ID = 'G-XVBZP28RD7';
  var KEY = 'amrisimply-consent';           /* 'granted' | 'denied' */
  var KEY_DATE = 'amrisimply-consent-date';
  var MAX_AGE_JOURS = 180;

  function lire(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function ecrire(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function effacer(k) { try { localStorage.removeItem(k); } catch (e) {} }

  function choixValide() {
    var v = lire(KEY);
    if (v !== 'granted' && v !== 'denied') return null;
    var t = parseInt(lire(KEY_DATE) || '0', 10);
    if (!t || (Date.now() - t) > MAX_AGE_JOURS * 864e5) {
      effacer(KEY); effacer(KEY_DATE);
      return null;
    }
    return v;
  }

  var gaCharge = false;
  function chargerGA() {
    if (gaCharge) return;
    gaCharge = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'granted'
    });
    window.gtag('js', new Date());
    window.gtag('config', ID);
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
    document.head.appendChild(s);
  }

  function accepter() {
    ecrire(KEY, 'granted'); ecrire(KEY_DATE, String(Date.now()));
    fermer();
    chargerGA();
  }
  function refuser() {
    ecrire(KEY, 'denied'); ecrire(KEY_DATE, String(Date.now()));
    fermer();
    if (gaCharge && window.gtag) {
      window.gtag('consent', 'update', { analytics_storage: 'denied' });
    }
  }

  var banniere = null;
  function fermer() {
    if (banniere) { banniere.remove(); banniere = null; }
  }

  function montrer() {
    if (banniere) return;
    var page = document.getElementById('page') || document.body;
    if (!document.getElementById('amrisimply-consent-style')) {
      var st = document.createElement('style');
      st.id = 'amrisimply-consent-style';
      st.textContent =
        '#amrisimply-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:9000;' +
        'max-width:520px;margin:0 auto;background:#16181D;color:#EDEFF3;' +
        'border:1px solid rgba(154,163,178,.25);border-radius:8px;padding:18px 20px;' +
        'font-size:14.5px;line-height:1.55;box-shadow:0 4px 24px rgba(0,0,0,.45)}' +
        '#amrisimply-consent p{margin:0 0 12px}' +
        '#amrisimply-consent a{color:#EDEFF3;text-decoration:underline}' +
        '#amrisimply-consent .cbtns{display:flex;gap:10px;flex-wrap:wrap}' +
        '#amrisimply-consent button{font:inherit;font-weight:600;border-radius:8px;' +
        'padding:10px 18px;cursor:pointer;border:1px solid transparent}' +
        '#amrisimply-consent .c-oui{background:#FF6152;color:#1B0704}' +
        '#amrisimply-consent .c-non{background:transparent;color:#EDEFF3;' +
        'border-color:rgba(154,163,178,.45)}';
      document.head.appendChild(st);
    }
    banniere = document.createElement('div');
    banniere.id = 'amrisimply-consent';
    banniere.setAttribute('role', 'region');
    banniere.setAttribute('aria-label', 'Cookies');
    banniere.innerHTML =
      '<p>' +
      '<span class="lg-fr">J’aimerais compter les visites avec Google Analytics, pour voir quelles pages t’aident vraiment. C’est anonyme pour moi, mais Google dépose un cookie. Tu choisis, et les deux boutons se valent. <a href="/#vie-privee">Vie privée</a></span>' +
      '<span class="lg-nl">Ik wil graag met Google Analytics tellen welke pagina’s je echt helpen. Voor mij anoniem, maar Google plaatst een cookie. Jij kiest, en beide knoppen zijn evenwaardig. <a href="/#vie-privee">Privacy</a></span>' +
      '</p>' +
      '<div class="cbtns">' +
      '<button type="button" class="c-oui"><span class="lg-fr">D’accord</span><span class="lg-nl">Oké</span></button>' +
      '<button type="button" class="c-non"><span class="lg-fr">Non merci</span><span class="lg-nl">Nee bedankt</span></button>' +
      '</div>';
    banniere.querySelector('.c-oui').addEventListener('click', accepter);
    banniere.querySelector('.c-non').addEventListener('click', refuser);
    page.appendChild(banniere);
  }

  /* Lien « Cookies » du pied de page : rouvre la question. */
  function initLiens() {
    var liens = document.querySelectorAll('[data-cookies]');
    for (var i = 0; i < liens.length; i++) {
      liens[i].addEventListener('click', function (e) {
        e.preventDefault();
        montrer();
      });
    }
  }

  function init() {
    initLiens();
    var choix = choixValide();
    if (choix === 'granted') { chargerGA(); return; }
    if (choix === 'denied') { return; }
    if (navigator.globalPrivacyControl === true) {
      ecrire(KEY, 'denied'); ecrire(KEY_DATE, String(Date.now()));
      return;
    }
    montrer();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
