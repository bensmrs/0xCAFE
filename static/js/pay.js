var stripe = null;
var mainElement = document.getElementById('main');
var payElement = document.getElementById('pay');
var amountElement = document.querySelector('#amount input');
var amountFormElement = document.querySelector('#amount-form');
var errorElement = document.getElementById('error');
var formElement = document.getElementById('form');
var backElement = document.getElementById('back');
var taxElement = document.getElementById('tax');
var card = null;

function _formatTime()
{
  [...document.getElementsByClassName('time')].forEach(e =>
  {
    let d = Date.parse(e.dataset.date);
    let delta = Date.now() - d;
    if (delta < 60 * 1000)
      e.innerHTML = "Il y a moins d’une minute";
    else if (delta < 60 * 60 * 1000)
    {
      const minutes = Math.round(delta/60000);
      if (minutes == 1)
        e.innerHTML = `Il y a une minute`;
      else
        e.innerHTML = `Il y a ${minutes} minutes`;
    }
    else
    {
      const days_ago = Math.floor(delta/86400000);
      switch (days_ago)
      {
      case 0:
        e.innerHTML = "Aujourd'hui à " + new Date(d).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        break;
      case 1:
        e.innerHTML = "Hier à " + new Date(d).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        break;
      case 2:
        e.innerHTML = "Avant-hier à " + new Date(d).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        break;
      default:
        e.innerHTML = new Date(d).toLocaleString([], {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute:'2-digit'})
      }
    }
  });
  [...document.getElementsByClassName('amount')].forEach(e => e.textContent = parseFloat(e.textContent).toLocaleString('fr-FR', { minimumFractionDigits: 2 }));
}

function _getPublicKey()
{
  return fetch('/public-key', { method: 'GET', headers: { 'Content-Type': 'application/json' } })
           .then(resp => resp.json())
           .then(data => data.publicKey);
}

function _pay(card, clientSecret)
{
  loading(true);
  stripe.confirmCardPayment(clientSecret, { payment_method: { card: card } })
    .then(resp =>
    {
      if (resp.error)
        showError(resp.error.message)
      else
        _orderComplete(resp.paymentIntent.id);
    });
}

function _orderComplete(paymentIntentId)
{
  loading(false);
  mainElement.className = 'done';
  payElement.onclick = () => window.location.reload();
}

function showError(errorMsg)
{
  loading(false);
  errorElement.textContent = errorMsg;
  errorElement.classList.remove('hidden');
  setTimeout(() => { errorElement.classList.add('hidden'); }, 4000);
}

function _showPaymentPrompt()
{
  loading(true);
  amountElement.disabled = true;
  amountElement.blur();
  mainElement.classList.add('full');
  fetch('/prepare-payment',
        { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount: parseFloat(amountElement.value) * 100 || 1000 }) })
    .then(resp => resp.json())
    .then(data =>
    {
      var elements = stripe.elements();
      card = elements.create('card');
      card.mount('#card');
      card.on('change',
              ev => { errorElement.textContent = ev.error ? ev.error.message : ''; });
      formElement.onsubmit = ev =>
      {
        ev.preventDefault();
        _pay(card, data.clientSecret);
      };
      payElement.onclick = () => _pay(card, data.clientSecret);
      mainElement.classList.add('loaded');
      loading(false);
    });
}

function loading(wanted)
{
  if (wanted)
    mainElement.classList.add('loading');
  else
    mainElement.classList.remove('loading');
}

function _cancel()
{
  mainElement.classList.remove('loaded');
  loading(true);
  payElement.onclick = _showPaymentPrompt;
  card.destroy();
  amountElement.disabled = false;
  mainElement.classList.remove('full');
  loading(false);
}

function _updateTax()
{
  let amount = parseFloat(amountElement.value) || 0;
  taxElement.textContent = Math.min((Math.round(amount * 1.4 + 25) / 100), amount).toLocaleString('fr-FR', { minimumFractionDigits: 2 });
}

function initStripe()
{
  loading(true);
  _formatTime();
  _getPublicKey().then(key => { stripe = Stripe(key); });
  payElement.onclick = _showPaymentPrompt;
  backElement.addEventListener('click', _cancel);
  amountFormElement.addEventListener('submit', ev =>
  {
    ev.preventDefault();
    _showPaymentPrompt();
  });
  amountElement.addEventListener('input', _updateTax);
  _updateTax();
  [...document.getElementsByClassName('button')].forEach(e => e.addEventListener('click', () => { amountElement.value = e.textContent; _updateTax(); }));
  loading(false);
}

initStripe();
