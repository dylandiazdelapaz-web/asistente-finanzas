const quizQuestions = [
  {
    prompt: 'Tus gastos superan tus ingresos este mes. ¿Qué conviene hacer primero?',
    options: ['Pedir un préstamo rápido para mantener todos los gastos', 'Revisar gastos, priorizar necesidades y ajustar los gastos prescindibles', 'Pagar solo una parte de las cuentas sin revisar intereses'],
    answer: 1,
    explanation: 'Un presupuesto realista parte por proteger necesidades y ajustar gastos antes de sumar deuda costosa.',
  },
  {
    prompt: '¿Para qué sirve principalmente un fondo de emergencia?',
    options: ['Cubrir imprevistos sin recurrir de inmediato a deuda', 'Obtener la mayor rentabilidad posible', 'Reemplazar todos los seguros'],
    answer: 0,
    explanation: 'Su objetivo es dar liquidez ante imprevistos. El monto depende de tus gastos esenciales y estabilidad de ingresos.',
  },
  {
    prompt: 'Si puedes pagar el total facturado de tu tarjeta de crédito, ¿qué suele convenir?',
    options: ['Pagar solo el mínimo para conservar efectivo', 'Pagar el total a tiempo para evitar intereses rotativos', 'Dejar el pago para el mes siguiente'],
    answer: 1,
    explanation: 'Pagar el total facturado a tiempo suele evitar los intereses por mantener saldo pendiente.',
  },
  {
    prompt: '¿Qué describe mejor la inflación?',
    options: ['Una caída general de precios que aumenta el costo de vida', 'Un aumento general de precios que reduce el poder de compra del dinero', 'Un impuesto aplicado únicamente a los ahorros'],
    answer: 1,
    explanation: 'Cuando suben los precios en general, con el mismo dinero normalmente puedes comprar menos.',
  },
  {
    prompt: '¿Qué busca la diversificación al invertir?',
    options: ['Repartir la exposición para reducir el riesgo de depender de un solo activo', 'Garantizar que nunca habrá pérdidas', 'Elegir siempre la inversión con mayor rentabilidad reciente'],
    answer: 0,
    explanation: 'Diversificar puede reducir el riesgo de concentración, pero no garantiza ganancias ni elimina todo riesgo.',
  },
  {
    prompt: '¿Qué puede ocurrir si durante mucho tiempo pagas solo el mínimo de una deuda?',
    options: ['La deuda se elimina automáticamente', 'Una mayor parte de los pagos puede ir a intereses y tardar más en bajar el saldo', 'El interés deja de aplicarse'],
    answer: 1,
    explanation: 'El pago mínimo evita caer en mora, pero puede alargar el pago y aumentar el costo total de la deuda.',
  },
  {
    prompt: '¿Qué significa el interés compuesto?',
    options: ['Recibir intereses solo una vez', 'Generar rendimientos también sobre intereses acumulados', 'Pagar siempre la misma cuota sin importar la tasa'],
    answer: 1,
    explanation: 'Con interés compuesto, los rendimientos acumulados también pueden generar nuevos rendimientos con el tiempo.',
  },
  {
    prompt: 'Al comparar dos créditos, ¿qué dato ayuda más a conocer su costo total?',
    options: ['Solo el valor de la cuota mensual', 'El costo total y la tasa o indicador anual comparable', 'El color de la tarjeta asociada'],
    answer: 1,
    explanation: 'Una cuota baja puede esconder un plazo largo. Compara el costo total y los indicadores de costo aplicables.',
  },
];

let quizIndex = 0;
let quizScore = 0;
let quizAnswered = false;
let quizAnswers = [];

const quizStage = document.getElementById('quiz-stage');
const quizResult = document.getElementById('quiz-result');
const quizPrompt = document.getElementById('quiz-prompt');
const quizOptions = document.getElementById('quiz-options');
const quizFeedback = document.getElementById('quiz-feedback');
const quizNextButton = document.getElementById('quiz-next');
const quizProgress = document.querySelector('.quiz-progress');

function showQuizQuestion() {
  const question = quizQuestions[quizIndex];
  quizAnswered = false;
  quizPrompt.textContent = question.prompt;
  document.getElementById('quiz-count').textContent = `Pregunta ${quizIndex + 1} de ${quizQuestions.length}`;
  quizProgress.setAttribute('aria-valuenow', String(quizIndex));
  document.getElementById('quiz-progress-fill').style.width = `${(quizIndex / quizQuestions.length) * 100}%`;
  quizFeedback.textContent = '';
  quizFeedback.className = 'quiz-feedback';
  quizNextButton.hidden = true;
  quizOptions.replaceChildren();

  question.options.forEach((option, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'quiz-option';
    button.textContent = option;
    button.addEventListener('click', () => answerQuizQuestion(index, button));
    quizOptions.appendChild(button);
  });
}

function answerQuizQuestion(selectedIndex, selectedButton) {
  if (quizAnswered) return;
  quizAnswered = true;
  quizAnswers[quizIndex] = selectedIndex;

  const question = quizQuestions[quizIndex];
  const options = [...quizOptions.querySelectorAll('button')];
  options.forEach((button, index) => {
    button.disabled = true;
    if (index === question.answer) button.classList.add('correct');
  });

  if (selectedIndex === question.answer) {
    quizScore += 1;
    quizFeedback.textContent = `Correcto. ${question.explanation}`;
    quizFeedback.className = 'quiz-feedback alert success show';
  } else {
    selectedButton.classList.add('incorrect');
    quizFeedback.textContent = `No exactamente. ${question.explanation}`;
    quizFeedback.className = 'quiz-feedback alert error show';
  }

  quizProgress.setAttribute('aria-valuenow', String(quizIndex + 1));
  document.getElementById('quiz-progress-fill').style.width = `${((quizIndex + 1) / quizQuestions.length) * 100}%`;
  quizNextButton.textContent = quizIndex === quizQuestions.length - 1 ? 'Ver mi resultado' : 'Siguiente pregunta';
  quizNextButton.hidden = false;
}

function finishQuiz() {
  quizStage.hidden = true;
  quizResult.hidden = false;
  document.getElementById('quiz-score').textContent = `Puntaje: ${quizScore} de ${quizQuestions.length}`;

  let level;
  let advice;
  if (quizScore <= 3) {
    level = 'Principiante';
    advice = 'Tienes una buena oportunidad para fortalecer conceptos básicos como presupuesto, ahorro y costo de las deudas.';
  } else if (quizScore <= 6) {
    level = 'En desarrollo';
    advice = 'Ya manejas varios conceptos importantes. Repasar inversión, inflación y comparación de créditos puede ayudarte a avanzar.';
  } else {
    level = 'Avanzado';
    advice = 'Muestras una comprensión sólida de estos conceptos. Sigue contrastando cada decisión con tus objetivos y circunstancias.';
  }

  document.getElementById('quiz-level').textContent = level;
  document.getElementById('quiz-advice').textContent = advice;
}

quizNextButton.addEventListener('click', () => {
  if (quizIndex < quizQuestions.length - 1) {
    quizIndex += 1;
    showQuizQuestion();
    quizPrompt.focus();
  } else {
    finishQuiz();
  }
});

document.getElementById('quiz-share').addEventListener('click', async function () {
  const status = document.getElementById('quiz-share-status');
  this.disabled = true;
  status.textContent = 'Compartiendo resultado...';

  try {
    const response = await fetch('/quiz-results', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        alias: document.getElementById('quiz-alias').value.trim() || null,
        answers: quizAnswers,
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'No se pudo compartir el resultado.');
    status.textContent = 'Resultado compartido. Gracias por participar.';
  } catch (error) {
    status.textContent = error.message;
    this.disabled = false;
  }
});

document.getElementById('quiz-restart').addEventListener('click', () => {
  quizIndex = 0;
  quizScore = 0;
  quizAnswers = [];
  document.getElementById('quiz-alias').value = '';
  document.getElementById('quiz-share').disabled = false;
  document.getElementById('quiz-share-status').textContent = '';
  quizResult.hidden = true;
  quizStage.hidden = false;
  showQuizQuestion();
});

document.getElementById('load-quiz-results').addEventListener('click', async () => {
  const status = document.getElementById('admin-status');
  const passwordInput = document.getElementById('admin-password');
  const summary = document.getElementById('admin-summary');
  const resultsList = document.getElementById('admin-results-list');
  status.textContent = 'Consultando...';

  try {
    const credentials = `admin:${passwordInput.value}`;
    const encodedCredentials = btoa(Array.from(new TextEncoder().encode(credentials), byte => String.fromCharCode(byte)).join(''));
    const response = await fetch('/admin/quiz-results', {
      headers: { Authorization: `Basic ${encodedCredentials}` },
    });
    const data = await response.json();
    if (!response.ok) {
      if (response.status === 401) passwordInput.value = '';
      throw new Error(data.detail || 'No se pudieron consultar los resultados.');
    }

    summary.replaceChildren();
    [['Respuestas', data.count], ['Principiante', data.by_level['Principiante']], ['En desarrollo', data.by_level['En desarrollo']], ['Avanzado', data.by_level['Avanzado']]].forEach(([label, value]) => {
      const metric = document.createElement('div');
      metric.className = 'metric';
      const metricLabel = document.createElement('div');
      metricLabel.className = 'metric-label';
      metricLabel.textContent = label;
      const metricValue = document.createElement('div');
      metricValue.className = 'metric-value';
      metricValue.textContent = value;
      metric.append(metricLabel, metricValue);
      summary.appendChild(metric);
    });

    resultsList.replaceChildren();
    data.results.forEach((result) => {
      const item = document.createElement('li');
      const name = document.createElement('span');
      name.textContent = result.alias || 'Anónimo';
      const detail = document.createElement('strong');
      detail.textContent = `${result.level} · ${result.score}/${result.total_questions} · ${result.created_at}`;
      item.append(name, detail);
      resultsList.appendChild(item);
    });

    summary.hidden = false;
    status.textContent = `Mostrando ${data.results.length} resultados recientes.`;
  } catch (error) {
    summary.hidden = true;
    resultsList.replaceChildren();
    status.textContent = error.message;
  }
});

showQuizQuestion();