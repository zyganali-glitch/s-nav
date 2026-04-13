const numberFormatter = new Intl.NumberFormat("tr-TR", {
  maximumFractionDigits: 2,
});

const dateFormatter = new Intl.DateTimeFormat("tr-TR", {
  dateStyle: "short",
  timeStyle: "short",
});

const NET_RULE_OPTIONS = [
  {
    code: "none",
    label: "Seçilmedi · net hesabı yapma",
    description: "Okuma yapılır, net alanları bilinçli olarak boş bırakılır.",
  },
  {
    code: "correct_only",
    label: "Net = doğru sayısı",
    description: "Yanlışlar netten düşülmez.",
  },
  {
    code: "minus_025",
    label: "4 yanlış 1 doğru götürür",
    description: "Net = doğru - (yanlış x 0.25)",
  },
  {
    code: "minus_0333",
    label: "3 yanlış 1 doğru götürür",
    description: "Net = doğru - (yanlış x 0.3333)",
  },
  {
    code: "minus_050",
    label: "2 yanlış 1 doğru götürür",
    description: "Net = doğru - (yanlış x 0.50)",
  },
  {
    code: "minus_100",
    label: "1 yanlış 1 doğru götürür",
    description: "Net = doğru - yanlış",
  },
];

const state = {
  exams: [],
  formTemplates: [],
  selectedExamCode: "",
  activeExamDetail: null,
  currentSession: null,
  operator: {
    netRuleCode: "none",
  },
  teacher: {
    isUploadingAnswerKey: false,
  },
  capture: {
    armed: false,
    keepBuffer: false,
    autoArm: true,
    idleMs: 900,
    isImporting: false,
    isReadingDevice: false,
    idleTimer: null,
    rawText: "",
  },
  form: {
    exam_code: "",
    title: "",
    description: "",
    exam_year: "",
    exam_term: "",
    exam_type: "",
    form_template_id: "varsayilan",
    booklet_codes: ["A"],
    questions: [],
  },
};

const dom = {
  examLibrary: document.getElementById("examLibrary"),
  refreshLibraryBtn: document.getElementById("refreshLibraryBtn"),
  loadStarterExamBtn: document.getElementById("loadStarterExamBtn"),
  jumpToOperatorBtn: document.getElementById("jumpToOperatorBtn"),
  libraryCountValue: document.getElementById("libraryCountValue"),
  selectedExamValue: document.getElementById("selectedExamValue"),
  sessionCountValue: document.getElementById("sessionCountValue"),
  newExamBtn: document.getElementById("newExamBtn"),
  saveExamBtn: document.getElementById("saveExamBtn"),
  examCodeInput: document.getElementById("examCodeInput"),
  examTitleInput: document.getElementById("examTitleInput"),
  examYearInput: document.getElementById("examYearInput"),
  examTermInput: document.getElementById("examTermInput"),
  examTypeInput: document.getElementById("examTypeInput"),
  examDescriptionInput: document.getElementById("examDescriptionInput"),
  bookletCodesInput: document.getElementById("bookletCodesInput"),
  formTemplateSelect: document.getElementById("formTemplateSelect"),
  answerKeyFileInput: document.getElementById("answerKeyFileInput"),
  uploadAnswerKeyBtn: document.getElementById("uploadAnswerKeyBtn"),
  answerKeyStatePill: document.getElementById("answerKeyStatePill"),
  answerKeyStatus: document.getElementById("answerKeyStatus"),
  addQuestionBtn: document.getElementById("addQuestionBtn"),
  questionBuilder: document.getElementById("questionBuilder"),
  operatorPanel: document.getElementById("operatorPanel"),
  feedbackBanner: document.getElementById("feedbackBanner"),
  operatorExamSelect: document.getElementById("operatorExamSelect"),
  operatorExamCodeInput: document.getElementById("operatorExamCodeInput"),
  operatorFormTemplateSelect: document.getElementById("operatorFormTemplateSelect"),
  deviceBookletOverrideSelect: document.getElementById("deviceBookletOverrideSelect"),
  netRuleSelect: document.getElementById("netRuleSelect"),
  operatorAnswerKeyStatus: document.getElementById("operatorAnswerKeyStatus"),
  importFileInput: document.getElementById("importFileInput"),
  runImportBtnTop: document.getElementById("runImportBtnTop"),
  runImportBtn: document.getElementById("runImportBtn"),
  readOpticalAnswerKeyBtn: document.getElementById("readOpticalAnswerKeyBtn"),
  deviceImportBtn: document.getElementById("deviceImportBtn"),
  armCaptureBtn: document.getElementById("armCaptureBtn"),
  importCapturedBtn: document.getElementById("importCapturedBtn"),
  clearCaptureBtn: document.getElementById("clearCaptureBtn"),
  captureInput: document.getElementById("captureInput"),
  captureModePill: document.getElementById("captureModePill"),
  captureStatsValue: document.getElementById("captureStatsValue"),
  captureStatusValue: document.getElementById("captureStatusValue"),
  captureFileNameInput: document.getElementById("captureFileNameInput"),
  deviceMaxSheetsInput: document.getElementById("deviceMaxSheetsInput"),
  deviceColumnsInput: document.getElementById("deviceColumnsInput"),
  deviceReadingMethodSelect: document.getElementById("deviceReadingMethodSelect"),
  deviceThicknessSelect: document.getElementById("deviceThicknessSelect"),
  deviceThresholdInput: document.getElementById("deviceThresholdInput"),
  deviceBacksideCheckbox: document.getElementById("deviceBacksideCheckbox"),
  captureIdleMsInput: document.getElementById("captureIdleMsInput"),
  autoArmCaptureCheckbox: document.getElementById("autoArmCaptureCheckbox"),
  keepCaptureBufferCheckbox: document.getElementById("keepCaptureBufferCheckbox"),
  deviceReadSummary: document.getElementById("deviceReadSummary"),
  deviceSheetTableWrap: document.getElementById("deviceSheetTableWrap"),
  dynamicImportHint: document.getElementById("dynamicImportHint"),
  summaryCards: document.getElementById("summaryCards"),
  reportMethodologyWrap: document.getElementById("reportMethodologyWrap"),
  bookletTableWrap: document.getElementById("bookletTableWrap"),
  groupTableWrap: document.getElementById("groupTableWrap"),
  questionTableWrap: document.getElementById("questionTableWrap"),
  questionChoiceTableWrap: document.getElementById("questionChoiceTableWrap"),
  studentTableWrap: document.getElementById("studentTableWrap"),
  studentAnswerMatrixWrap: document.getElementById("studentAnswerMatrixWrap"),
  recentSessions: document.getElementById("recentSessions"),
  assessmentHighlights: document.getElementById("assessmentHighlights"),
  exportCsvBtn: document.getElementById("exportCsvBtn"),
  exportXlsxBtn: document.getElementById("exportXlsxBtn"),
  exportTxtBtn: document.getElementById("exportTxtBtn"),
  exportPdfBtn: document.getElementById("exportPdfBtn"),
  exportJsonBtn: document.getElementById("exportJsonBtn"),
  statusPill: document.getElementById("statusPill"),
  questionCardTemplate: document.getElementById("questionCardTemplate"),
};

function normalizeToken(value) {
  return String(value || "")
    .trim()
    .toUpperCase()
    .replace(/[^A-Z0-9_-]+/g, "");
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatNumber(value) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberFormatter.format(numberValue) : "—";
}

function formatPercent(value) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? `${numberFormatter.format(numberValue)}%` : "—";
}

function formatDateTime(value) {
  if (!value) {
    return "—";
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? String(value) : dateFormatter.format(parsed);
}

function formatCellValue(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  if (typeof value === "number") {
    return formatNumber(value);
  }
  if (Array.isArray(value)) {
    return value.length ? value.map((item) => formatCellValue(item)).join(", ") : "—";
  }
  if (typeof value === "object") {
    const entries = Object.entries(value);
    return entries.length
      ? entries.map(([key, item]) => `${key}: ${formatCellValue(item)}`).join(" · ")
      : "—";
  }
  return String(value);
}

function forceLtrText(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  return `\u200e${String(value)}`;
}

function formatExamMetadata(exam) {
  const parts = [exam?.exam_year, exam?.exam_term, exam?.exam_type]
    .map((item) => String(item || "").trim())
    .filter(Boolean);
  return parts.join(" · ") || "Metadata yok";
}

function createDefaultQuestion(index, bookletCodes = state.form.booklet_codes) {
  const bookletMappings = {};
  bookletCodes.forEach((booklet) => {
    bookletMappings[booklet] = { position: index, correct_answer: "" };
  });
  return {
    canonical_no: index,
    group_label: "Genel",
    weight: 1,
    booklet_mappings: bookletMappings,
  };
}

function createStarterExamPayload() {
  return {
    exam_code: "DENEME01",
    title: "Nisan Denemesi",
    description: "Örnek iki kitapçıklı deneme sınavı",
    exam_year: "2026",
    exam_term: "Bahar",
    exam_type: "Deneme",
    form_template_id: "varsayilan",
    booklet_codes: ["A", "B"],
    questions: [
      {
        canonical_no: 1,
        group_label: "Türkçe",
        weight: 5,
        booklet_mappings: {
          A: { position: 1, correct_answer: "A" },
          B: { position: 2, correct_answer: "A" },
        },
      },
      {
        canonical_no: 2,
        group_label: "Matematik",
        weight: 5,
        booklet_mappings: {
          A: { position: 2, correct_answer: "D" },
          B: { position: 1, correct_answer: "D" },
        },
      },
      {
        canonical_no: 3,
        group_label: "Fen",
        weight: 5,
        booklet_mappings: {
          A: { position: 3, correct_answer: "B" },
          B: { position: 4, correct_answer: "B" },
        },
      },
      {
        canonical_no: 4,
        group_label: "Sosyal",
        weight: 5,
        booklet_mappings: {
          A: { position: 4, correct_answer: "C" },
          B: { position: 3, correct_answer: "C" },
        },
      },
    ],
  };
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Beklenmeyen hata" }));
    throw new Error(payload.detail || payload.message || "Beklenmeyen hata");
  }
  return response.json();
}

async function requestBlob(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Beklenmeyen hata" }));
    throw new Error(payload.detail || payload.message || "Beklenmeyen hata");
  }
  return response;
}

function resolveCurrentSessionId() {
  return state.currentSession?.session_id || state.activeExamDetail?.recent_sessions?.[0]?.session_id || "latest";
}

function parseDownloadFileName(contentDisposition, fallbackName) {
  const match = String(contentDisposition || "").match(/filename="?([^";]+)"?/i);
  return match?.[1] || fallbackName;
}

function getDefaultFormTemplate() {
  return state.formTemplates.find((item) => item.is_default) || state.formTemplates[0] || {
    id: "varsayilan",
    name: "Varsayılan",
    is_default: true,
  };
}

function getFormTemplateName(templateId) {
  const selectedId = String(templateId || "").trim() || getDefaultFormTemplate().id;
  return state.formTemplates.find((item) => item.id === selectedId)?.name || getDefaultFormTemplate().name;
}

function getActiveFormTemplateId() {
  return String(
    dom.operatorFormTemplateSelect?.value
    || dom.formTemplateSelect.value
    || state.form.form_template_id
    || getDefaultFormTemplate().id
  ).trim() || getDefaultFormTemplate().id;
}

function renderNetRuleSelect(selectedCode = state.operator.netRuleCode) {
  const normalized = NET_RULE_OPTIONS.some((item) => item.code === selectedCode) ? selectedCode : "none";
  dom.netRuleSelect.innerHTML = NET_RULE_OPTIONS
    .map((item) => `<option value="${escapeHtml(item.code)}">${escapeHtml(item.label)}</option>`)
    .join("");
  dom.netRuleSelect.value = normalized;
  state.operator.netRuleCode = normalized;
}

function getSelectedNetRuleCode() {
  return dom.netRuleSelect?.value || state.operator.netRuleCode || "none";
}

function hasAnswerKeyLoaded() {
  const activeQuestionCount = Number(state.activeExamDetail?.questions?.length || 0);
  const draftQuestionCount = Number((state.form.questions || []).length || 0);
  return Math.max(activeQuestionCount, draftQuestionCount) > 0;
}

function renderFormTemplateSelect() {
  const templates = state.formTemplates.length ? state.formTemplates : [getDefaultFormTemplate()];
  const defaultTemplate = getDefaultFormTemplate();
  const selectedId = templates.some((item) => item.id === state.form.form_template_id)
    ? state.form.form_template_id
    : defaultTemplate.id;
  const optionsHtml = templates
    .map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.name)}</option>`)
    .join("");

  state.form.form_template_id = selectedId;
  dom.formTemplateSelect.innerHTML = optionsHtml;
  dom.formTemplateSelect.value = selectedId;
  dom.operatorFormTemplateSelect.innerHTML = optionsHtml;
  dom.operatorFormTemplateSelect.value = selectedId;
}

function handleFormTemplateChange(source) {
  const selectedId = String(
    source === "operator"
      ? dom.operatorFormTemplateSelect.value
      : dom.formTemplateSelect.value
  ).trim() || getDefaultFormTemplate().id;
  const persistedId = String(
    state.activeExamDetail?.active_form_template?.id
    || state.activeExamDetail?.form_template_id
    || ""
  ).trim();
  const selectedName = getFormTemplateName(selectedId);

  state.form.form_template_id = selectedId;
  renderFormTemplateSelect();
  renderImportHint();
  renderActionStates();

  if (source === "operator") {
    const isTemporaryOverride = Boolean(state.form.exam_code && persistedId && persistedId !== selectedId);
    setFeedback(
      isTemporaryOverride
        ? `${selectedName} okutma formatı seçildi. Bu okumada format override uygulanacak; kalıcı olması için sınavı yeniden kaydet.`
        : `${selectedName} aktif okutma formatı olarak seçildi.`,
      isTemporaryOverride ? "warn" : "success"
    );
  }
}

function renderDeviceBookletOverrideSelect() {
  const booklets = state.form.booklet_codes.length ? state.form.booklet_codes : ["A"];
  dom.deviceBookletOverrideSelect.innerHTML = [
    '<option value="">Otomatik algıla</option>',
    ...booklets.map((booklet) => `<option value="${escapeHtml(booklet)}">${escapeHtml(booklet)} kitapçığı</option>`),
  ].join("");
}

function renderAnswerKeyStatus() {
  const questionCount = state.form.questions.length;
  const profile = state.activeExamDetail?.answer_key_profile || {};
  const opticalReadyBooklets = state.activeExamDetail?.summary?.optical_answer_key_ready_count || 0;
  const opticalReadyNames = state.activeExamDetail?.summary?.optical_answer_key_ready_booklets || [];
  const totalBooklets = state.form.booklet_codes.length;

  if (!questionCount && !opticalReadyBooklets) {
    dom.answerKeyStatePill.textContent = "Henüz yüklenmedi";
    dom.answerKeyStatePill.className = "status-pill is-warn";
    dom.answerKeyStatus.innerHTML = '<p class="muted-copy">Bu sınav için cevap anahtarı hazır değil. Operatör tarafında okutma ve puanlama, cevap anahtarı yüklenmeden açılmayacak.</p>';
    dom.operatorAnswerKeyStatus.textContent = "Cevap anahtarı henüz yok. Önce operatör optik formu kodlayıp okutmalı veya yedek olarak teacher anahtarı yüklenmeli.";
    return;
  }

  if (!questionCount && opticalReadyBooklets) {
    dom.answerKeyStatePill.textContent = `${formatNumber(opticalReadyBooklets)}/${formatNumber(totalBooklets)} kitapçık`; 
    dom.answerKeyStatePill.className = "status-pill is-warn";
    dom.answerKeyStatus.innerHTML = `
      <p class="muted-copy">Optik cevap anahtarı kısmen alındı. Hazır kitapçıklar: ${escapeHtml(opticalReadyNames.join(", ") || "- ")}. Kalan kitapçıklar okunduktan sonra puanlama açılacak.</p>
    `;
    dom.operatorAnswerKeyStatus.textContent = `${opticalReadyNames.join(", ")} kitapçığı hafızaya alındı. Puanlama için tüm kitapçıkların optik anahtarı tamamlanmalı.`;
    return;
  }

  const strategyLabels = {
    detailed: "Detaylı eşleme",
    sequential: "Sıralı cevap anahtarı",
    manual: "Form düzenleyici",
  };
  const strategy = strategyLabels[profile.booklet_strategy] || "Yüklü cevap anahtarı";
  const sourceLabel = profile.source_label || "Form düzenleyici";
  const sourceFile = profile.source_file || "Elle düzenlenen soru kartları";
  const updatedAt = profile.updated_at ? formatDateTime(profile.updated_at) : "Henüz kaydedilmedi";

  dom.answerKeyStatePill.textContent = `${formatNumber(questionCount)} soru hazır`;
  dom.answerKeyStatePill.className = "status-pill is-success";
  dom.answerKeyStatus.innerHTML = `
    <div class="answer-key-summary-grid">
      <article class="summary-card mini-card">
        <p class="section-kicker">Kaynak</p>
        <strong>${escapeHtml(sourceLabel)}</strong>
      </article>
      <article class="summary-card mini-card">
        <p class="section-kicker">Mod</p>
        <strong>${escapeHtml(strategy)}</strong>
      </article>
      <article class="summary-card mini-card">
        <p class="section-kicker">Dosya</p>
        <strong>${escapeHtml(sourceFile)}</strong>
      </article>
      <article class="summary-card mini-card">
        <p class="section-kicker">Güncelleme</p>
        <strong>${escapeHtml(updatedAt)}</strong>
      </article>
    </div>
  `;
  dom.operatorAnswerKeyStatus.textContent = `${questionCount} soruluk cevap anahtarı hazır. Operatör artık tepsiyi SR-3500 üzerinden okuyup doğrudan puanlayabilir.`;
}

function setFeedback(message, tone = "warn") {
  dom.feedbackBanner.textContent = message;
  dom.feedbackBanner.className = `feedback-banner ${tone === "success" ? "is-success" : "is-warn"}`;
}

function setStatus(label, tone = "warn") {
  dom.statusPill.textContent = label;
  dom.statusPill.className = `status-pill ${tone === "success" ? "is-success" : "is-warn"}`;
}

function setCaptureStatus(label, tone = "warn") {
  dom.captureStatusValue.textContent = label;
  dom.captureModePill.textContent = state.capture.armed ? "Okumaya hazır" : "Beklemede";
  dom.captureModePill.className = `status-pill ${tone === "success" ? "is-success" : "is-warn"}`;
}

function getCaptureRows(text) {
  return String(text || "")
    .replaceAll("\r\n", "\n")
    .replaceAll("\r", "\n")
    .split("\n")
    .map((line) => line.trimEnd())
    .filter((line) => line.trim());
}

function renderHeroMetrics() {
  dom.libraryCountValue.textContent = formatNumber(state.exams.length);
  dom.selectedExamValue.textContent = state.selectedExamCode || "Yok";
  const sessionCount = state.activeExamDetail?.recent_sessions?.length || 0;
  dom.sessionCountValue.textContent = formatNumber(sessionCount);
}

function renderExamSelect() {
  if (!state.exams.length) {
    dom.operatorExamSelect.innerHTML = '<option value="">Önce sınav oluştur veya örnek sınav yükle</option>';
    dom.operatorExamSelect.value = "";
    return;
  }

  dom.operatorExamSelect.innerHTML = state.exams
    .map((exam) => `<option value="${escapeHtml(exam.exam_code)}">${escapeHtml(exam.exam_code)} · ${escapeHtml(exam.title)}</option>`)
    .join("");

  dom.operatorExamSelect.value = state.selectedExamCode || state.exams[0].exam_code;
}

function renderCaptureStats() {
  const rows = getCaptureRows(dom.captureInput.value);
  dom.captureStatsValue.textContent = `${formatNumber(rows.length)} satır`;
}

function collectDeviceReadSettings() {
  return {
    max_sheets: Math.max(0, Number(dom.deviceMaxSheetsInput.value || 0)),
    columns: Math.min(48, Math.max(1, Number(dom.deviceColumnsInput.value || 48))),
    reading_method: Math.min(6, Math.max(1, Number(dom.deviceReadingMethodSelect.value || 3))),
    thickness_type: Math.min(5, Math.max(0, Number(dom.deviceThicknessSelect.value || 0))),
    backside_reading: dom.deviceBacksideCheckbox.checked,
    analysis_threshold: Math.min(16, Math.max(1, Number(dom.deviceThresholdInput.value || 12))),
  };
}

function renderDeviceReadAnalysis(metadata) {
  const sheets = metadata?.sheets || [];
  if (!sheets.length) {
    dom.deviceReadSummary.innerHTML = '<div class="empty-state">Okumaya uygun form bulunamadı.</div>';
    dom.deviceSheetTableWrap.innerHTML = '<div class="empty-state">Henüz cihaz okuması yapılmadı.</div>';
    return;
  }

  const totalCandidates = sheets.reduce((sum, sheet) => sum + Number(sheet.candidate_mark_count || 0), 0);
  const totalNonzero = sheets.reduce((sum, sheet) => sum + Number(sheet.nonzero_cell_count || 0), 0);
  const settings = metadata.settings || {};

  dom.deviceReadSummary.innerHTML = [
    ["Form", formatNumber(metadata.sheet_count || sheets.length)],
    ["Aday işaret", formatNumber(totalCandidates)],
    ["Karanlık hücre", formatNumber(totalNonzero)],
    ["Yöntem / kolon", `${formatNumber(settings.reading_method || 3)} / ${formatNumber(settings.columns || 48)}`],
  ]
    .map(
      ([label, value]) => `
        <article class="summary-card">
          <p class="section-kicker">${escapeHtml(label)}</p>
          <strong>${escapeHtml(value)}</strong>
        </article>
      `
    )
    .join("");

  renderTable(
    dom.deviceSheetTableWrap,
    [
      { label: "Form", render: (row) => `#${row.sheet_no}` },
      { label: "Boyut", render: (row) => `${row.rows}x${row.columns}` },
      { label: "Aday işaret", render: (row) => formatNumber(row.candidate_mark_count) },
      { label: "Karanlık hücre", render: (row) => formatNumber(row.nonzero_cell_count) },
      { label: "Maks. yoğunluk", render: (row) => formatNumber(row.darkest_value) },
      { label: "Önizleme", render: (row) => (row.preview || []).join(" | ") || "Belirgin işaret yok" },
    ],
    sheets,
    "Henüz cihaz okuması yapılmadı."
  );
}

function scheduleCaptureIdleState() {
  if (state.capture.idleTimer) {
    window.clearTimeout(state.capture.idleTimer);
  }
  if (!state.capture.armed) {
    return;
  }
  state.capture.idleTimer = window.setTimeout(() => {
    if (!state.capture.armed) {
      return;
    }
    if (getCaptureRows(dom.captureInput.value).length) {
      setCaptureStatus("Veri akışı durdu. İçe aktarabilirsin.", "success");
    } else {
      setCaptureStatus("Hâlâ veri bekleniyor", "warn");
    }
  }, state.capture.idleMs);
}

function appendCaptureText(text) {
  if (!text) {
    return;
  }
  dom.captureInput.value += text;
  renderCaptureStats();
  setCaptureStatus("Veri alınıyor", "success");
  renderActionStates();
  scheduleCaptureIdleState();
}

function handleGlobalCaptureKeydown(event) {
  if (!state.capture.armed || state.capture.isImporting) {
    return;
  }
  if (event.ctrlKey && event.key === "Enter") {
    event.preventDefault();
    importCapturedBuffer().catch(showError);
    return;
  }
  if (event.key === "Escape") {
    event.preventDefault();
    clearCaptureBuffer();
    return;
  }
  if (event.altKey || event.metaKey) {
    return;
  }

  const target = event.target;
  const isEditable = target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target?.isContentEditable;
  if (isEditable && target !== dom.captureInput) {
    return;
  }

  if (event.key === "Enter" || event.key === "Tab") {
    event.preventDefault();
    appendCaptureText("\n");
    return;
  }
  if (event.key === "Backspace") {
    event.preventDefault();
    dom.captureInput.value = dom.captureInput.value.slice(0, -1);
    renderCaptureStats();
    renderActionStates();
    scheduleCaptureIdleState();
    return;
  }
  if (event.key.length === 1) {
    event.preventDefault();
    appendCaptureText(event.key);
  }
}

function focusCaptureInput() {
  dom.captureInput.focus();
  dom.captureInput.select();
}

function renderActionStates() {
  const activeExamCode = normalizeToken(dom.operatorExamSelect.value || dom.operatorExamCodeInput.value || state.form.exam_code);
  const hasImportFile = Boolean(dom.importFileInput.files?.length);
  const hasAnswerKeyFile = Boolean(dom.answerKeyFileInput.files?.length);
  const hasCaptureRows = getCaptureRows(dom.captureInput.value).length > 0;
  const isSaveReady = normalizeToken(dom.examCodeInput.value) && dom.examTitleInput.value.trim().length >= 2;
  const hasAnswerKey = hasAnswerKeyLoaded();
  const hasSession = Boolean(resolveCurrentSessionId() && activeExamCode);

  dom.saveExamBtn.disabled = !isSaveReady;
  dom.uploadAnswerKeyBtn.disabled = !isSaveReady || !hasAnswerKeyFile || state.teacher.isUploadingAnswerKey;
  dom.readOpticalAnswerKeyBtn.disabled = !activeExamCode || state.capture.isReadingDevice;
  dom.deviceImportBtn.disabled = !activeExamCode || !hasAnswerKey || state.capture.isReadingDevice;
  dom.runImportBtnTop.disabled = !(activeExamCode && hasImportFile && hasAnswerKey);
  dom.runImportBtn.disabled = !(activeExamCode && hasImportFile && hasAnswerKey);
  dom.armCaptureBtn.disabled = !activeExamCode || state.capture.isReadingDevice;
  dom.importCapturedBtn.disabled = !(activeExamCode && hasCaptureRows && hasAnswerKey) || state.capture.isImporting;
  dom.clearCaptureBtn.disabled = !dom.captureInput.value.length;
  dom.exportCsvBtn.disabled = !hasSession;
  dom.exportXlsxBtn.disabled = !hasSession;
  dom.exportTxtBtn.disabled = !hasSession;
  dom.exportPdfBtn.disabled = !hasSession;
  dom.exportJsonBtn.disabled = !hasSession;
}

async function requestDeviceRead() {
  const examCode = normalizeToken(dom.operatorExamSelect.value || dom.operatorExamCodeInput.value || state.form.exam_code);
  if (!examCode) {
    throw new Error("Önce bir sınav seçmeden SR-3500 okutma komutu gönderilemez.");
  }
  if (state.capture.isReadingDevice) {
    return;
  }

  state.capture.isReadingDevice = true;
  state.capture.armed = true;
  const settings = collectDeviceReadSettings();
  renderActionStates();
  setCaptureStatus("SR-3500 komutu gönderildi, tepsi okunuyor", "success");
  setFeedback("Ham cihaz analizi başlatıldı. Bu adım cevap anahtarından bağımsızdır; uygulama tepsiyi okuyup matris ve işaret özetini gösterecek.", "success");

  try {
    const payload = await requestJson("/api/device/mark-read", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ settings }),
    });

    state.capture.rawText = payload.raw_text || "";
    dom.captureInput.value = payload.analysis_text || payload.raw_text || "";
    renderCaptureStats();
    renderActionStates();
    renderDeviceReadAnalysis(payload.metadata || null);

    const sheetCount = Number(payload.metadata?.sheet_count || 0);
    setCaptureStatus(`${formatNumber(sheetCount)} form okundu`, "success");
    setFeedback(`SR-3500 toplu okuma tamamlandı. ${formatNumber(sheetCount)} form için cihaz analizi üretildi.`, "success");
  } finally {
    state.capture.isReadingDevice = false;
    state.capture.armed = false;
    renderActionStates();
  }
}

async function requestDeviceAnswerKeyRead() {
  const examCode = normalizeToken(dom.operatorExamSelect.value || dom.operatorExamCodeInput.value || state.form.exam_code);
  if (!examCode) {
    throw new Error("Önce bir sınav seçmeden optik cevap anahtarı okutulamaz.");
  }
  if (state.capture.isReadingDevice) {
    return;
  }

  state.capture.isReadingDevice = true;
  renderActionStates();
  setStatus("Optik cevap anahtarı okunuyor", "success");
  setFeedback("Operatör cevap anahtarı okutma akışı başlatıldı. Cihazdan gelen ilk form mevcut sınavın anahtar hafızasına yazılacak.", "success");

  try {
    const bookletCode = normalizeToken(dom.deviceBookletOverrideSelect.value);
    const payload = await requestJson(`/api/exams/${encodeURIComponent(examCode)}/device-answer-key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        settings: collectDeviceReadSettings(),
        booklet_code: bookletCode || null,
        form_template_id: getActiveFormTemplateId(),
      }),
    });

    state.capture.rawText = payload.device?.raw_text || "";
    dom.captureInput.value = payload.device?.analysis_text || "";
    renderCaptureStats();
    renderDeviceReadAnalysis(payload.device?.metadata || null);
    state.currentSession = null;
    fillForm(payload.exam);

    const processedBooklets = payload.processed_booklets || [];
    const detectedBooklet = processedBooklets.join(", ") || payload.decoded_sheet?.booklet_code || bookletCode || "?";
    const readyCount = payload.exam?.answer_key_profile?.ready_booklet_count || payload.exam?.summary?.optical_answer_key_ready_count || 0;
    const totalCount = payload.exam?.answer_key_profile?.total_booklet_count || state.form.booklet_codes.length || processedBooklets.length;
    const questionCount = payload.exam?.summary?.question_count || payload.decoded_sheet?.decoded_question_count || 0;
    setStatus("Optik cevap anahtarı alındı", "success");
    if (processedBooklets.length > 1) {
      setFeedback(`${detectedBooklet} kitapçıkları hafızaya alındı. Hazır durum: ${formatNumber(readyCount)}/${formatNumber(totalCount)} kitapçık.`, "success");
    } else if (questionCount && readyCount >= totalCount) {
      setFeedback(`${detectedBooklet} kitapçığı tamamlandı. ${formatNumber(questionCount)} soruluk cevap anahtarı artık tepsi puanlamaya hazır.`, "success");
    } else {
      setFeedback(`${detectedBooklet} kitapçığı hafızaya alındı. Hazır durum: ${formatNumber(readyCount)}/${formatNumber(totalCount)} kitapçık.`, "success");
    }
  } finally {
    state.capture.isReadingDevice = false;
    renderActionStates();
  }
}

async function requestDeviceImport() {
  const examCode = normalizeToken(dom.operatorExamSelect.value || dom.operatorExamCodeInput.value || state.form.exam_code);
  if (!examCode) {
    throw new Error("Önce bir sınav seçmeden tepsi puanlama başlatılamaz.");
  }
  if (!hasAnswerKeyLoaded()) {
    throw new Error("Tepsi puanlamadan önce optik veya dosya tabanlı cevap anahtarı tamamlanmalıdır.");
  }
  if (state.capture.isReadingDevice) {
    return;
  }

  state.capture.isReadingDevice = true;
  renderActionStates();
  setStatus("Tepsi okunuyor ve puanlanıyor", "success");
  setFeedback("SR-3500 tepsisi seçilen format ve hazır cevap anahtarıyla puanlanıyor.", "success");

  try {
    const payload = await requestJson(`/api/exams/${encodeURIComponent(examCode)}/device-import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        settings: collectDeviceReadSettings(),
        form_template_id: getActiveFormTemplateId(),
        net_rule_code: getSelectedNetRuleCode(),
      }),
    });

    state.capture.rawText = payload.device?.raw_text || "";
    dom.captureInput.value = payload.device?.analysis_text || "";
    renderCaptureStats();
    renderDeviceReadAnalysis(payload.device?.metadata || null);
    state.currentSession = payload.session;
    await selectExam(examCode);
    renderAnalytics(payload.session);
    setStatus("Tepsi puanlandı", "success");
    setFeedback(`Cihazdan okunan ${formatNumber(payload.session?.summary?.student_count || 0)} form puanlandı ve son oturuma işlendi.`, "success");
  } finally {
    state.capture.isReadingDevice = false;
    renderActionStates();
  }
}

function armCaptureMode() {
  const examCode = normalizeToken(dom.operatorExamSelect.value || dom.operatorExamCodeInput.value || state.form.exam_code);
  if (!examCode) {
    throw new Error("Önce bir sınav seçmeden canlı okuma başlatılamaz.");
  }
  if (!hasAnswerKeyLoaded()) {
    throw new Error("Cevap anahtarı yüklenmeden canlı okuma modu açılmaz.");
  }
  state.capture.armed = true;
  setCaptureStatus("Okuyucudan veri bekleniyor", "success");
  setFeedback("Canlı dinleme başladı. Tarayıcı sekmesini açık bırakıp formu okut.", "success");
  renderActionStates();
  scheduleCaptureIdleState();
  focusCaptureInput();
}

function disarmCaptureMode(label = "Hazır") {
  state.capture.armed = false;
  if (state.capture.idleTimer) {
    window.clearTimeout(state.capture.idleTimer);
    state.capture.idleTimer = null;
  }
  setCaptureStatus(label, "warn");
  renderActionStates();
}

function clearCaptureBuffer() {
  state.capture.rawText = "";
  dom.captureInput.value = "";
  renderCaptureStats();
  setCaptureStatus(state.capture.armed ? "Alan temizlendi, okuma hazır" : "Alan temizlendi", state.capture.armed ? "success" : "warn");
  scheduleCaptureIdleState();
  renderActionStates();
}

async function importCapturedBuffer() {
  const examCode = normalizeToken(dom.operatorExamSelect.value || dom.operatorExamCodeInput.value || state.form.exam_code);
  const captureText = dom.captureInput.value;
  const rows = getCaptureRows(captureText);
  if (!examCode) {
    throw new Error("Canlı okumayı içe aktarmak için önce sınav seçilmelidir.");
  }
  if (!rows.length) {
    throw new Error("İçe aktarılacak okuma verisi bulunamadı.");
  }
  if (!hasAnswerKeyLoaded()) {
    throw new Error("Cevap anahtarı yüklenmeden okutulan veri puanlanamaz.");
  }
  if (state.capture.isImporting) {
    return;
  }

  state.capture.isImporting = true;
  renderActionStates();
  setCaptureStatus("Okunan veriler işleniyor", "success");

  try {
    const fileName = (dom.captureFileNameInput.value || "sr3500-live.txt").trim() || "sr3500-live.txt";
    const payload = state.capture.rawText
      ? await requestJson(`/api/exams/${encodeURIComponent(examCode)}/device-import`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_text: state.capture.rawText,
          settings: collectDeviceReadSettings(),
          form_template_id: getActiveFormTemplateId(),
          net_rule_code: getSelectedNetRuleCode(),
        }),
      })
      : await (async () => {
        const formData = new FormData();
        formData.append("file", new File([captureText], fileName, { type: "text/plain" }));
        formData.append("net_rule_code", getSelectedNetRuleCode());
        return requestJson(`/api/exams/${encodeURIComponent(examCode)}/imports`, {
          method: "POST",
          body: formData,
        });
      })();

    state.currentSession = payload.session;
    await selectExam(examCode);
    renderAnalytics(payload.session);
    setCaptureStatus(`${rows.length} satır içe aktarıldı`, "success");

    if (!state.capture.keepBuffer) {
      state.capture.rawText = "";
      dom.captureInput.value = "";
      renderCaptureStats();
    }
    if (state.capture.autoArm) {
      armCaptureMode();
    }
  } finally {
    state.capture.isImporting = false;
    renderActionStates();
  }
}

function syncBookletsFromInput() {
  const bookletCodes = dom.bookletCodesInput.value
    .split(",")
    .map((item) => normalizeToken(item))
    .filter(Boolean)
    .filter((item, index, list) => list.indexOf(item) === index);

  state.form.booklet_codes = bookletCodes.length ? bookletCodes : ["A"];
  state.form.questions = state.form.questions.map((question, index) => {
    const bookletMappings = {};
    state.form.booklet_codes.forEach((booklet) => {
      bookletMappings[booklet] = question.booklet_mappings[booklet] || {
        position: index + 1,
        correct_answer: "",
      };
    });
    return { ...question, booklet_mappings: bookletMappings };
  });

  renderQuestionBuilder();
  renderAnswerKeyStatus();
  renderImportHint();
}

function renderLibrary() {
  if (!state.exams.length) {
    dom.examLibrary.innerHTML = `
      <section class="empty-library-card">
        <h3>Henüz kayıtlı sınav yok</h3>
        <p>Hızlı başlamak için örnek sınav yükleyebilir veya sağdaki formdan yeni sınav oluşturabilirsin.</p>
        <div class="empty-state-actions">
          <button class="primary-button" type="button" data-action="load-starter">Örnek sınav yükle</button>
          <button class="ghost-button" type="button" data-action="new-exam">Yeni sınav oluştur</button>
        </div>
      </section>
    `;
    renderHeroMetrics();
    renderExamSelect();
    return;
  }

  dom.examLibrary.innerHTML = state.exams
    .map((exam) => {
      const activeClass = exam.exam_code === state.selectedExamCode ? "active" : "";
      return `
        <article class="library-card ${activeClass}" data-exam-code="${escapeHtml(exam.exam_code)}">
          <div class="library-card-top">
            <p class="section-kicker">${escapeHtml(exam.exam_code)}</p>
            <div class="library-card-actions">
              <span class="library-chip">${escapeHtml(formatNumber(exam.session_count))} oturum</span>
              <button class="ghost-button library-delete-btn" type="button" data-delete-exam="${escapeHtml(exam.exam_code)}">Sil</button>
            </div>
          </div>
          <h3>${escapeHtml(exam.title)}</h3>
          <p>${escapeHtml(exam.description || "Açıklama girilmedi")}</p>
          <div class="library-card-meta">
            <strong>${escapeHtml(formatNumber(exam.question_count))} soru</strong>
            <span>${escapeHtml((exam.booklet_codes || []).join(", ") || "Tek kitapçık")}</span>
            <span>${escapeHtml(exam.form_template_name || "Varsayılan")}</span>
            <span>${escapeHtml(exam.has_answer_key ? "Anahtar hazır" : "Anahtar yok")}</span>
            <span>${escapeHtml(formatExamMetadata(exam))}</span>
          </div>
        </article>
      `;
    })
    .join("");

  renderHeroMetrics();
  renderExamSelect();
}

function renderQuestionBuilder() {
  dom.questionBuilder.innerHTML = "";

  if (!state.form.questions.length) {
    dom.questionBuilder.innerHTML = '<div class="empty-state">İlk soruyu ekleyerek kitapçık sırasını tanımla.</div>';
    return;
  }

  state.form.questions.forEach((question, questionIndex) => {
    const fragment = dom.questionCardTemplate.content.cloneNode(true);
    const title = fragment.querySelector(".question-title");
    const removeButton = fragment.querySelector(".remove-question-btn");
    const bookletGrid = fragment.querySelector(".booklet-grid");

    title.textContent = `Soru ${question.canonical_no}`;
    removeButton.dataset.questionIndex = String(questionIndex);

    fragment.querySelector('[data-field="canonical_no"]').value = question.canonical_no;
    fragment.querySelector('[data-field="canonical_no"]').dataset.questionIndex = String(questionIndex);
    fragment.querySelector('[data-field="group_label"]').value = question.group_label;
    fragment.querySelector('[data-field="group_label"]').dataset.questionIndex = String(questionIndex);
    fragment.querySelector('[data-field="weight"]').value = question.weight;
    fragment.querySelector('[data-field="weight"]').dataset.questionIndex = String(questionIndex);

    state.form.booklet_codes.forEach((booklet) => {
      const mapping = question.booklet_mappings[booklet] || { position: questionIndex + 1, correct_answer: "" };
      const block = document.createElement("div");
      block.className = "booklet-mini-card";
      block.innerHTML = `
        <h4>${escapeHtml(booklet)} kitapçığı</h4>
        <label>
          <span>Soru sırası</span>
          <input type="number" min="1" data-question-index="${questionIndex}" data-booklet="${escapeHtml(booklet)}" data-map-field="position" value="${escapeHtml(mapping.position)}">
        </label>
        <label>
          <span>Doğru cevap</span>
          <input type="text" maxlength="4" data-question-index="${questionIndex}" data-booklet="${escapeHtml(booklet)}" data-map-field="correct_answer" value="${escapeHtml(mapping.correct_answer)}" placeholder="A, B, C, D">
        </label>
      `;
      bookletGrid.appendChild(block);
    });

    dom.questionBuilder.appendChild(fragment);
  });
}

function renderImportHint() {
  const questionCount = state.form.questions.length || 0;
  const opticalReadyCount = Number(state.activeExamDetail?.summary?.optical_answer_key_ready_count || 0);
  const totalBooklets = state.form.booklet_codes.length || 0;
  const bookletText = state.form.booklet_codes.join(", ") || "A";
  const templateName = getFormTemplateName(state.form.form_template_id);

  dom.dynamicImportHint.textContent = questionCount
    ? `Bu sınav için ${questionCount} soru, ${bookletText} kitapçıkları ve ${templateName} optik formatı hazır. Operatör tarafı artık bu cevap anahtarı olmadan okutmaya açılmaz.`
    : opticalReadyCount
      ? `Bu sınav için ${templateName} optik formatında ${opticalReadyCount}/${totalBooklets} kitapçığın optik cevap anahtarı alındı. Kalan kitapçıklar tamamlanınca puanlama açılacak.`
      : `Bu sınav için ${templateName} optik formatı seçildi ama cevap anahtarı henüz yok. Öncelikli yol operatörün optik cevap anahtarını okutmasıdır; gerekirse teacher panelinden yedek cevap anahtarı yüklenebilir.`;
}

function renderSummaryCards(session) {
  const summary = session?.summary || null;
  if (!summary) {
    dom.summaryCards.innerHTML = '<div class="empty-state">İçe aktarma sonrası genel özet kartları burada görünür.</div>';
    return;
  }

  dom.summaryCards.innerHTML = [
    ["Öğrenci", formatNumber(summary.student_count)],
    ["Toplam soru", formatNumber(summary.total_questions)],
    ["Ortalama puan", formatNumber(summary.average_score)],
    ["Ort. doğru", formatNumber(summary.average_correct_count)],
    ["Ort. yanlış", formatNumber(summary.average_wrong_count)],
    ["Ort. net", formatNumber(summary.average_net_count)],
    ["Net kuralı", session?.net_policy?.label || summary.net_policy_label || "Belirtilmedi"],
    ["Ort. yüzde", formatPercent(summary.average_percent)],
    ["Tamamlama", formatPercent(summary.completion_rate)],
    ["Alpha", formatNumber(summary.reliability_alpha)],
    ["Atlanan satır", formatNumber(summary.skipped_rows)],
  ]
    .map(
      ([label, value]) => `
        <article class="summary-card">
          <p class="section-kicker">${escapeHtml(label)}</p>
          <strong>${escapeHtml(value)}</strong>
        </article>
      `
    )
    .join("");
}

function renderAssessmentHighlights(session) {
  const highlights = session?.assessment_highlights || {};
  const hardest = (highlights.hardest_questions || []).slice(0, 3).map((item) => `S${item.canonical_no}`).join(", ") || "—";
  const easiest = (highlights.easiest_questions || []).slice(0, 3).map((item) => `S${item.canonical_no}`).join(", ") || "—";
  const blanks = (highlights.most_blank_questions || []).slice(0, 3).map((item) => `S${item.canonical_no}`).join(", ") || "—";
  const weak = (highlights.weak_discrimination_questions || []).slice(0, 3).map((item) => `S${item.canonical_no}`).join(", ") || "—";
  const topStudents = (highlights.top_students || []).slice(0, 3).map((item) => `#${item.exam_rank} ${item.student_id}`).join(", ") || "—";
  const lowestStudents = (highlights.lowest_students || []).slice(0, 3).map((item) => `#${item.exam_rank} ${item.student_id}`).join(", ") || "—";

  if (!session) {
    dom.assessmentHighlights.innerHTML = '<div class="empty-state">Henüz içe aktarma yapılmadı.</div>';
    return;
  }

  dom.assessmentHighlights.innerHTML = [
    ["En zor", hardest],
    ["En kolay", easiest],
    ["En çok boş", blanks],
    ["Ayırt ediciliği zayıf", weak],
    ["Üst performans", topStudents],
    ["Alt performans", lowestStudents],
  ]
    .map(
      ([label, value]) => `
        <article class="summary-card">
          <p class="section-kicker">${escapeHtml(label)}</p>
          <strong>${escapeHtml(value)}</strong>
        </article>
      `
    )
    .join("");
}

function renderReportMethodology(session) {
  const glossary = session?.analysis_glossary || [];
  const commentary = session?.academic_commentary || [];
  if (!session) {
    dom.reportMethodologyWrap.innerHTML = '<div class="empty-state">Henüz içe aktarma yapılmadı.</div>';
    return;
  }

  const rows = [
    ...commentary.map((item) => ({
      kind: "Akademik yorum",
      term: item.title,
      production: item.text,
      usage: "",
    })),
    ...glossary.map((item) => ({
      kind: "Metodoloji",
      term: item.term,
      production: item.how,
      usage: [item.why, item.value_use].filter(Boolean).join(" "),
    })),
  ];

  renderTable(
    dom.reportMethodologyWrap,
    [
      { label: "Tür", key: "kind" },
      { label: "Gösterge", key: "term" },
      { label: "Üretim özeti", key: "production" },
      { label: "Kullanım ve yorum", key: "usage" },
    ],
    rows,
    "Metodoloji bilgisi yok."
  );
}

function formatChoiceDistribution(row, choice) {
  const distribution = row.choice_distribution?.[choice];
  if (!distribution) {
    return "—";
  }
  return `${formatNumber(distribution.count)} / ${formatPercent(distribution.rate)}`;
}

function renderTable(container, headers, rows, emptyMessage) {
  if (!rows || !rows.length) {
    container.innerHTML = `<div class="empty-state">${escapeHtml(emptyMessage)}</div>`;
    return;
  }

  const headerHtml = headers.map((header) => `<th>${escapeHtml(header.label)}</th>`).join("");
  const rowHtml = rows
    .map((row) => {
      const cells = headers
        .map((header) => {
          const rawValue = typeof header.render === "function" ? header.render(row) : row[header.key];
          return `<td>${escapeHtml(formatCellValue(rawValue))}</td>`;
        })
        .join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");

  container.innerHTML = `<table><thead><tr>${headerHtml}</tr></thead><tbody>${rowHtml}</tbody></table>`;
}

function getQuestionNumbers(session) {
  const numbers = (session?.question_summary || [])
    .map((item) => Number(item.canonical_no))
    .filter((item) => Number.isFinite(item));
  if (numbers.length) {
    return numbers;
  }
  const firstStudent = (session?.student_results || session?.student_preview || [])[0];
  return (firstStudent?.question_responses || [])
    .map((item) => Number(item.canonical_no))
    .filter((item) => Number.isFinite(item));
}

function buildResponseLookup(row) {
  return Object.fromEntries(
    (row?.question_responses || []).map((item) => [Number(item.canonical_no), item.display_value || item.marked_answer || "-(B)"])
  );
}

function renderStudentAnswerMatrix(session) {
  const rows = session?.student_results || session?.student_preview || [];
  const questionNumbers = getQuestionNumbers(session);
  if (!rows.length || !questionNumbers.length) {
    dom.studentAnswerMatrixWrap.innerHTML = '<div class="empty-state">Öğrenci cevap matrisi içe aktarma sonrası burada görünür.</div>';
    return;
  }

  const enrichedRows = rows.map((row) => ({ ...row, __responseLookup: buildResponseLookup(row) }));
  renderTable(
    dom.studentAnswerMatrixWrap,
    [
      { label: "Genel sıra", render: (row) => formatNumber(row.exam_rank) },
      { label: "Öğrenci", key: "student_id" },
      { label: "Ad soyad", render: (row) => row.student_full_name || `${row.student_name || ""} ${row.student_surname || ""}`.trim() || "—" },
      { label: "Sınıf", render: (row) => row.classroom || "—" },
      { label: "Kitapçık", key: "booklet_code" },
      ...questionNumbers.map((questionNo) => ({
        label: `S${questionNo}`,
        render: (row) => row.__responseLookup?.[questionNo] || "-(B)",
      })),
    ],
    enrichedRows,
    "Öğrenci cevap matrisi yok."
  );
}

function renderRecentSessions() {
  const sessions = state.activeExamDetail?.recent_sessions || [];
  if (!sessions.length) {
    dom.recentSessions.innerHTML = '<div class="empty-state">Bu sınav için henüz oturum yok.</div>';
    renderHeroMetrics();
    return;
  }

  dom.recentSessions.innerHTML = sessions
    .map(
      (session) => `
        <article class="session-card">
          <p class="section-kicker">${escapeHtml(session.session_id)}</p>
          <strong>${escapeHtml(session.source_file)}</strong>
          <p>${escapeHtml(formatNumber(session.summary.student_count))} öğrenci · ort. ${escapeHtml(formatNumber(session.summary.average_score))} puan</p>
          <small>${escapeHtml(formatDateTime(session.created_at))}</small>
        </article>
      `
    )
    .join("");

  renderHeroMetrics();
}

function renderAnalytics(session) {
  state.currentSession = session || null;
  if (session?.net_policy?.code) {
    renderNetRuleSelect(session.net_policy.code);
  }
  renderSummaryCards(session || null);
  renderReportMethodology(session || null);
  renderAssessmentHighlights(session || null);

  renderTable(
    dom.bookletTableWrap,
    [
      { label: "Kitapçık", key: "booklet_code" },
      { label: "Öğrenci", render: (row) => formatNumber(row.student_count) },
      { label: "Toplam puan", render: (row) => formatNumber(row.total_score) },
      { label: "Toplam doğru", render: (row) => formatNumber(row.total_correct_count) },
      { label: "Toplam yanlış", render: (row) => formatNumber(row.total_wrong_count) },
      { label: "Toplam boş", render: (row) => formatNumber(row.total_blank_count) },
      { label: "Toplam net", render: (row) => formatNumber(row.total_net_count) },
      { label: "Ort. puan", render: (row) => formatNumber(row.average_score) },
      { label: "Maks.", render: (row) => formatNumber(row.max_score) },
      { label: "Ort. doğru", render: (row) => formatNumber(row.average_correct_count) },
      { label: "Ort. yanlış", render: (row) => formatNumber(row.average_wrong_count) },
      { label: "Ort. boş", render: (row) => formatNumber(row.average_blank_count) },
      { label: "Ort. net", render: (row) => formatNumber(row.average_net_count) },
      { label: "Ort. doğruluk", render: (row) => formatPercent(row.average_accuracy_percent) },
    ],
    session?.booklet_summary || [],
    "Kitapçık bazlı analiz yok."
  );

  renderTable(
    dom.groupTableWrap,
    [
      { label: "Grup", key: "group_label" },
      { label: "Öğrenci", render: (row) => formatNumber(row.student_count) },
      { label: "Soru", render: (row) => formatNumber(row.question_count) },
      { label: "Toplam puan", render: (row) => formatNumber(row.total_score) },
      { label: "Toplam doğru", render: (row) => formatNumber(row.total_correct_count) },
      { label: "Toplam yanlış", render: (row) => formatNumber(row.total_wrong_count) },
      { label: "Toplam boş", render: (row) => formatNumber(row.total_blank_count) },
      { label: "Toplam net", render: (row) => formatNumber(row.total_net_count) },
      { label: "Ort. puan", render: (row) => formatNumber(row.average_score) },
      { label: "Ort. doğru", render: (row) => formatNumber(row.average_correct_count) },
      { label: "Ort. yanlış", render: (row) => formatNumber(row.average_wrong_count) },
      { label: "Ort. boş", render: (row) => formatNumber(row.average_blank_count) },
      { label: "Ort. net", render: (row) => formatNumber(row.average_net_count) },
      { label: "Maks.", render: (row) => formatNumber(row.max_score) },
      { label: "Ort. doğruluk", render: (row) => formatPercent(row.average_accuracy_percent) },
    ],
    session?.group_summary || [],
    "Grup analizi yok."
  );

  renderTable(
    dom.questionTableWrap,
    [
      { label: "Soru", render: (row) => `S${row.canonical_no}` },
      { label: "Grup", key: "group_label" },
      { label: "Ağırlık", render: (row) => formatNumber(row.weight) },
      { label: "Doğru oran", render: (row) => formatPercent(row.correct_rate) },
      { label: "Yanlış oran", render: (row) => formatPercent(row.wrong_rate) },
      { label: "Boş oran", render: (row) => formatPercent(row.blank_rate) },
      { label: "Güçlük indeksi", render: (row) => formatNumber(row.difficulty_index) },
      { label: "Madde varyansı", render: (row) => formatNumber(row.item_variance) },
      { label: "Madde std sapması", render: (row) => formatNumber(row.item_std_dev) },
      { label: "Nokta-çift serili r", render: (row) => formatNumber(row.point_biserial) },
      { label: "r yorumu", render: (row) => row.point_biserial_label || "—" },
      { label: "Üst grup %", render: (row) => formatPercent(row.upper_group_correct_rate) },
      { label: "Alt grup %", render: (row) => formatPercent(row.lower_group_correct_rate) },
      { label: "Ayırt indeksi", render: (row) => formatNumber(row.discrimination_index) },
      { label: "Güçlük", render: (row) => row.difficulty_label || "—" },
      { label: "Ayırt edicilik", render: (row) => row.discrimination_label || "—" },
      {
        label: "Kitapçık sırası",
        render: (row) => Object.entries(row.booklet_positions || {})
          .map(([booklet, position]) => `${booklet}:${position}`)
          .join(" | "),
      },
      {
        label: "Anahtar",
        render: (row) => Object.entries(row.booklet_answer_key || {})
          .map(([booklet, answer]) => `${booklet}:${answer}`)
          .join(" | "),
      },
      {
        label: "Kitapçık dağılımı",
        render: (row) => Object.entries(row.booklets || {})
          .map(([booklet, stats]) => `${booklet}: D ${formatPercent(stats.correct_rate)} / Y ${formatPercent(stats.wrong_rate)}`)
          .join(" | "),
      },
    ],
    session?.question_summary || [],
    "Soru analizi yok."
  );

  renderTable(
    dom.questionChoiceTableWrap,
    [
      { label: "Soru", render: (row) => `S${row.canonical_no}` },
      { label: "Grup", key: "group_label" },
      { label: "Ağırlık", render: (row) => formatNumber(row.weight) },
      { label: "Öğrenci", render: (row) => formatNumber(row.student_count) },
      { label: "A", render: (row) => formatChoiceDistribution(row, "A") },
      { label: "B", render: (row) => formatChoiceDistribution(row, "B") },
      { label: "C", render: (row) => formatChoiceDistribution(row, "C") },
      { label: "D", render: (row) => formatChoiceDistribution(row, "D") },
      { label: "E", render: (row) => formatChoiceDistribution(row, "E") },
      { label: "Boş", render: (row) => `${formatNumber(row.blank_distribution?.count)} / ${formatPercent(row.blank_distribution?.rate)}` },
      { label: "Doğru oran", render: (row) => formatPercent(row.correct_rate) },
      { label: "Yanlış oran", render: (row) => formatPercent(row.wrong_rate) },
      { label: "Güçlük indeksi", render: (row) => formatNumber(row.difficulty_index) },
      { label: "Madde varyansı", render: (row) => formatNumber(row.item_variance) },
      { label: "Madde std sapması", render: (row) => formatNumber(row.item_std_dev) },
      { label: "Nokta-çift serili r", render: (row) => formatNumber(row.point_biserial) },
      { label: "r yorumu", render: (row) => row.point_biserial_label || "—" },
      { label: "Üst grup %", render: (row) => formatPercent(row.upper_group_correct_rate) },
      { label: "Alt grup %", render: (row) => formatPercent(row.lower_group_correct_rate) },
      { label: "Ayırt indeksi", render: (row) => formatNumber(row.discrimination_index) },
      { label: "Güçlük", render: (row) => row.difficulty_label || "—" },
      { label: "Ayırt edicilik", render: (row) => row.discrimination_label || "—" },
      {
        label: "Kitapçık sırası",
        render: (row) => Object.entries(row.booklet_positions || {}).map(([booklet, position]) => `${booklet}:${position}`).join(" | "),
      },
      {
        label: "Anahtar",
        render: (row) => Object.entries(row.booklet_answer_key || {}).map(([booklet, answer]) => `${booklet}:${answer}`).join(" | "),
      },
    ],
    session?.question_summary || [],
    "Şık bazlı soru dağılımı yok."
  );

  renderTable(
    dom.studentTableWrap,
    [
      { label: "Öğrenci", key: "student_id" },
      { label: "Ad soyad", render: (row) => row.student_full_name || `${row.student_name || ""} ${row.student_surname || ""}`.trim() || "—" },
      { label: "Sınıf", render: (row) => forceLtrText(row.classroom || row.class_number || "") },
      { label: "Kitapçık", key: "booklet_code" },
      { label: "Form kodu", render: (row) => forceLtrText(row.scanned_exam_code || "") },
      { label: "Form tarihi", render: (row) => forceLtrText(row.scanned_exam_date || row.decoded_fields?.exam_date || "") },
      { label: "Puan", render: (row) => formatNumber(row.score) },
      { label: "Yüzde", render: (row) => formatPercent(row.weighted_percent) },
      { label: "Doğru", render: (row) => formatNumber(row.correct_count) },
      { label: "Yanlış", render: (row) => formatNumber(row.wrong_count) },
      { label: "Boş", render: (row) => formatNumber(row.blank_count) },
      { label: "Net", render: (row) => formatNumber(row.net_count) },
      { label: "Toplam", render: (row) => formatNumber(row.total_questions) },
      { label: "Genel sıra", render: (row) => formatNumber(row.exam_rank) },
      { label: "Sınıf sıra", render: (row) => formatNumber(row.class_rank) },
    ],
    session?.student_results || session?.student_preview || [],
    "Öğrenci önizlemi yok."
  );

  renderStudentAnswerMatrix(session || null);

  setStatus(session ? "İçe aktarma tamamlandı" : "Hazır", session ? "success" : "warn");
  renderHeroMetrics();
}

function fillForm(examDetail) {
  const exam = examDetail || null;
  const defaultTemplate = getDefaultFormTemplate();
  state.activeExamDetail = exam;
  state.selectedExamCode = exam?.exam_code || "";
  state.form.exam_code = exam?.exam_code || "";
  state.form.title = exam?.title || "";
  state.form.description = exam?.description || "";
  state.form.exam_year = exam?.exam_year || "";
  state.form.exam_term = exam?.exam_term || "";
  state.form.exam_type = exam?.exam_type || "";
  state.form.form_template_id = exam?.form_template_id || defaultTemplate.id;
  state.form.booklet_codes = exam?.booklet_codes?.length ? [...exam.booklet_codes] : ["A"];
  state.form.questions = exam?.questions?.length
    ? exam.questions.map((question) => ({
      canonical_no: question.canonical_no,
      group_label: question.group_label,
      weight: question.weight,
      booklet_mappings: structuredClone(question.booklet_mappings),
    }))
    : [];

  dom.examCodeInput.value = state.form.exam_code;
  dom.examTitleInput.value = state.form.title;
  dom.examYearInput.value = state.form.exam_year;
  dom.examTermInput.value = state.form.exam_term;
  dom.examTypeInput.value = state.form.exam_type;
  dom.examDescriptionInput.value = state.form.description;
  dom.bookletCodesInput.value = state.form.booklet_codes.join(", ");
  dom.operatorExamCodeInput.value = state.form.exam_code;
  renderFormTemplateSelect();
  renderNetRuleSelect();

  renderLibrary();
  renderExamSelect();
  renderDeviceBookletOverrideSelect();
  renderQuestionBuilder();
  renderAnswerKeyStatus();
  renderImportHint();
  renderCaptureStats();
  renderDeviceReadAnalysis(null);
  renderRecentSessions();
  renderHeroMetrics();

  if (!state.currentSession) {
    renderAnalytics(null);
  }

  if (state.capture.autoArm && state.form.exam_code && hasAnswerKeyLoaded()) {
    armCaptureMode();
  } else {
    disarmCaptureMode("Hazır");
  }

  setFeedback(
    state.form.exam_code
      ? hasAnswerKeyLoaded()
        ? `${state.form.exam_code} seçildi. Cevap anahtarı hazır; okutma veya dosya içe aktarma yapabilirsin.`
        : `${state.form.exam_code} seçildi. Önce cevap anahtarını yükle, sonra operatör okutmaya geçsin.`
      : "Dosya okumak için önce sınav seç, ardından dosyayı seçip içe aktarma butonuna bas.",
    state.form.exam_code && hasAnswerKeyLoaded() ? "success" : "warn"
  );
  renderActionStates();
}

function collectFormPayload() {
  return {
    exam_code: normalizeToken(dom.examCodeInput.value),
    title: dom.examTitleInput.value.trim(),
    description: dom.examDescriptionInput.value.trim(),
    exam_year: dom.examYearInput.value.trim(),
    exam_term: dom.examTermInput.value.trim(),
    exam_type: dom.examTypeInput.value.trim(),
    form_template_id: dom.formTemplateSelect.value || getDefaultFormTemplate().id,
    booklet_codes: state.form.booklet_codes,
    questions: state.form.questions.map((question) => ({
      canonical_no: Number(question.canonical_no),
      group_label: question.group_label,
      weight: Number(question.weight),
      booklet_mappings: Object.fromEntries(
        state.form.booklet_codes.map((booklet) => [booklet, {
          position: Number(question.booklet_mappings[booklet]?.position || 0),
          correct_answer: normalizeToken(question.booklet_mappings[booklet]?.correct_answer || ""),
        }])
      ),
    })),
  };
}

async function loadExamLibrary() {
  const payload = await requestJson("/api/exams");
  state.exams = payload.items || [];
  renderLibrary();
  renderExamSelect();
  renderHeroMetrics();
}

async function loadFormTemplates() {
  const payload = await requestJson("/api/form-templates");
  state.formTemplates = payload.items || [];
  renderFormTemplateSelect();
}

async function selectExam(examCode) {
  if (!examCode) {
    state.currentSession = null;
    fillForm(null);
    return;
  }

  const detail = await requestJson(`/api/exams/${encodeURIComponent(examCode)}`);
  fillForm(detail);
  if (detail.recent_sessions?.length) {
    renderAnalytics(detail.recent_sessions[0]);
  } else {
    renderAnalytics(null);
  }
}

async function handleSaveExam() {
  syncBookletsFromInput();
  const payload = collectFormPayload();
  const detail = await requestJson("/api/exams", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  await loadExamLibrary();
  state.currentSession = null;
  fillForm(detail);
  setStatus(payload.questions.length ? "Sınav kaydedildi" : "Sınav taslağı kaydedildi", "success");
  setFeedback(
    payload.questions.length
      ? "Sınav ve cevap anahtarı kaydedildi. Operatör bu sınavı artık kullanabilir."
      : "Sınav taslağı kaydedildi. Şimdi cevap anahtarı dosyasını yükleyebilirsin.",
    "success"
  );
}

async function handleAnswerKeyUpload() {
  const file = dom.answerKeyFileInput.files?.[0];
  if (!file) {
    throw new Error("Önce cevap anahtarı dosyası seçilmelidir.");
  }

  state.teacher.isUploadingAnswerKey = true;
  renderActionStates();

  try {
    syncBookletsFromInput();
    const draftPayload = collectFormPayload();
    const savedDraft = await requestJson("/api/exams", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(draftPayload),
    });

    const formData = new FormData();
    formData.append("file", file);

    const detail = await requestJson(`/api/exams/${encodeURIComponent(savedDraft.exam_code)}/answer-key`, {
      method: "POST",
      body: formData,
    });

    await loadExamLibrary();
    state.currentSession = null;
    fillForm(detail);
    setStatus("Cevap anahtarı yüklendi", "success");
    setFeedback(`${file.name} işlendi. Soru kartları cevap anahtarından otomatik üretildi.`, "success");
  } finally {
    state.teacher.isUploadingAnswerKey = false;
    renderActionStates();
  }
}

async function loadStarterExam() {
  const payload = createStarterExamPayload();
  const detail = await requestJson("/api/exams", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await loadExamLibrary();
  state.currentSession = null;
  fillForm(detail);
  setStatus("Örnek sınav hazırlandı", "success");
}

async function handleImport() {
  const examCode = normalizeToken(dom.operatorExamSelect.value || dom.operatorExamCodeInput.value || state.form.exam_code);
  const file = dom.importFileInput.files[0];
  if (!examCode) {
    throw new Error("Dosya içe aktarmadan önce bir sınav seçilmelidir.");
  }
  if (!file) {
    throw new Error("İçe aktarılacak dosya seçilmelidir.");
  }
  if (!hasAnswerKeyLoaded()) {
    throw new Error("Cevap anahtarı yüklenmeden öğrenci cevapları puanlanamaz.");
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("net_rule_code", getSelectedNetRuleCode());
  const payload = await requestJson(`/api/exams/${encodeURIComponent(examCode)}/imports`, {
    method: "POST",
    body: formData,
  });

  state.currentSession = payload.session;
  await selectExam(examCode);
  renderAnalytics(payload.session);
  setFeedback(`${file.name} işlendi. Analiz alanı güncellendi.`, "success");
}

async function handleDeleteExam(examCode) {
  const normalizedExamCode = normalizeToken(examCode);
  if (!normalizedExamCode) {
    throw new Error("Silinecek sınav kodu bulunamadı.");
  }
  const approved = window.confirm(`${normalizedExamCode} kalıcı olarak silinsin mi? Bu işlem sınav oturumlarını da kaldırır.`);
  if (!approved) {
    return;
  }

  await requestJson(`/api/exams/${encodeURIComponent(normalizedExamCode)}`, { method: "DELETE" });
  if (state.selectedExamCode === normalizedExamCode) {
    state.currentSession = null;
    fillForm(null);
  }
  await loadExamLibrary();
  if (state.exams.length) {
    await selectExam(state.exams[0].exam_code);
  }
  setFeedback(`${normalizedExamCode} sınavı silindi.`, "success");
}

async function downloadSessionExport(exportFormat) {
  const examCode = normalizeToken(dom.operatorExamSelect.value || dom.operatorExamCodeInput.value || state.form.exam_code);
  if (!examCode) {
    throw new Error("Export için önce bir sınav seçilmelidir.");
  }

  const sessionId = resolveCurrentSessionId();
  const response = await requestBlob(
    `/api/exams/${encodeURIComponent(examCode)}/exports/${encodeURIComponent(exportFormat)}?session_id=${encodeURIComponent(sessionId)}`
  );
  const blob = await response.blob();
  const fileName = parseDownloadFileName(response.headers.get("Content-Disposition"), `${examCode}.${exportFormat}`);
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = downloadUrl;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(downloadUrl);
  setFeedback(`${fileName} indirildi.`, "success");
}

function resetForm() {
  state.currentSession = null;
  dom.importFileInput.value = "";
  dom.answerKeyFileInput.value = "";
  fillForm(null);
  renderActionStates();
}

function bindEvents() {
  dom.refreshLibraryBtn.addEventListener("click", () => loadExamLibrary().catch(showError));
  dom.loadStarterExamBtn.addEventListener("click", () => loadStarterExam().catch(showError));
  dom.jumpToOperatorBtn.addEventListener("click", () => {
    dom.operatorPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  dom.newExamBtn.addEventListener("click", resetForm);
  dom.saveExamBtn.addEventListener("click", () => handleSaveExam().catch(showError));
  dom.uploadAnswerKeyBtn.addEventListener("click", () => handleAnswerKeyUpload().catch(showError));
  dom.readOpticalAnswerKeyBtn.addEventListener("click", () => requestDeviceAnswerKeyRead().catch(showError));
  dom.deviceImportBtn.addEventListener("click", () => requestDeviceImport().catch(showError));
  dom.addQuestionBtn.addEventListener("click", () => {
    state.form.questions.push(createDefaultQuestion(state.form.questions.length + 1));
    renderQuestionBuilder();
    renderAnswerKeyStatus();
    renderImportHint();
    renderActionStates();
  });
  dom.bookletCodesInput.addEventListener("change", () => {
    syncBookletsFromInput();
    renderActionStates();
  });
  dom.runImportBtn.addEventListener("click", () => handleImport().catch(showError));
  dom.runImportBtnTop.addEventListener("click", () => handleImport().catch(showError));
  dom.armCaptureBtn.addEventListener("click", () => requestDeviceRead().catch(showError));
  dom.importCapturedBtn.addEventListener("click", () => importCapturedBuffer().catch(showError));
  dom.clearCaptureBtn.addEventListener("click", clearCaptureBuffer);

  dom.captureInput.addEventListener("focus", () => {
    if (!hasAnswerKeyLoaded()) {
      setCaptureStatus("Önce cevap anahtarı yüklenmeli", "warn");
      renderActionStates();
      return;
    }
    state.capture.armed = true;
    setCaptureStatus("Okuyucudan veri bekleniyor", "success");
    scheduleCaptureIdleState();
    renderActionStates();
  });

  dom.captureInput.addEventListener("blur", () => {
    if (state.capture.armed && !state.capture.isImporting) {
      setCaptureStatus("Odak değişti ama dinleme sürüyor", "success");
    }
  });

  dom.captureInput.addEventListener("input", () => {
    state.capture.rawText = "";
    renderCaptureStats();
    if (state.capture.armed) {
      setCaptureStatus("Veri alınıyor", "success");
      scheduleCaptureIdleState();
    }
    renderActionStates();
  });

  dom.captureInput.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault();
      clearCaptureBuffer();
      return;
    }
    if (event.key === "Enter" && event.ctrlKey) {
      event.preventDefault();
      importCapturedBuffer().catch(showError);
    }
  });

  dom.captureIdleMsInput.addEventListener("input", () => {
    state.capture.idleMs = Math.max(250, Number(dom.captureIdleMsInput.value || 900));
  });

  dom.autoArmCaptureCheckbox.addEventListener("change", () => {
    state.capture.autoArm = dom.autoArmCaptureCheckbox.checked;
  });

  dom.keepCaptureBufferCheckbox.addEventListener("change", () => {
    state.capture.keepBuffer = dom.keepCaptureBufferCheckbox.checked;
  });

  dom.formTemplateSelect.addEventListener("change", () => {
    handleFormTemplateChange("teacher");
  });

  dom.operatorFormTemplateSelect.addEventListener("change", () => {
    handleFormTemplateChange("operator");
  });

  dom.netRuleSelect.addEventListener("change", () => {
    state.operator.netRuleCode = dom.netRuleSelect.value || "none";
    const selectedRule = NET_RULE_OPTIONS.find((item) => item.code === state.operator.netRuleCode);
    setFeedback(selectedRule?.description || "Net kuralı güncellendi.", "success");
  });

  dom.answerKeyFileInput.addEventListener("change", () => {
    const file = dom.answerKeyFileInput.files?.[0];
    setFeedback(
      file
        ? `${file.name} cevap anahtarı dosyası seçildi. İstersen sınav taslağını aynı adımda kaydedip yükleyebilirim.`
        : "Cevap anahtarı dosyası seçimi temizlendi.",
      file ? "success" : "warn"
    );
    renderActionStates();
  });

  document.addEventListener("keydown", handleGlobalCaptureKeydown, true);

  dom.importFileInput.addEventListener("change", renderActionStates);
  dom.exportCsvBtn.addEventListener("click", () => downloadSessionExport("csv").catch(showError));
  dom.exportXlsxBtn.addEventListener("click", () => downloadSessionExport("xlsx").catch(showError));
  dom.exportTxtBtn.addEventListener("click", () => downloadSessionExport("txt").catch(showError));
  dom.exportPdfBtn.addEventListener("click", () => downloadSessionExport("pdf").catch(showError));
  dom.exportJsonBtn.addEventListener("click", () => downloadSessionExport("json").catch(showError));
  dom.importFileInput.addEventListener("change", () => {
    const file = dom.importFileInput.files?.[0];
    setFeedback(file ? `${file.name} seçildi. Şimdi "Seçili dosyayı oku" butonuna bas.` : "Dosya seçimi temizlendi.", file ? "success" : "warn");
    renderActionStates();
  });
  dom.operatorExamSelect.addEventListener("change", () => {
    selectExam(dom.operatorExamSelect.value).catch(showError);
  });
  dom.deviceBookletOverrideSelect.addEventListener("change", renderActionStates);
  dom.operatorExamCodeInput.addEventListener("input", renderActionStates);

  dom.examLibrary.addEventListener("click", (event) => {
    const actionButton = event.target.closest("[data-action]");
    if (actionButton) {
      const { action } = actionButton.dataset;
      if (action === "load-starter") {
        loadStarterExam().catch(showError);
      }
      if (action === "new-exam") {
        resetForm();
      }
      return;
    }

    const deleteButton = event.target.closest("[data-delete-exam]");
    if (deleteButton) {
      event.stopPropagation();
      handleDeleteExam(deleteButton.dataset.deleteExam).catch(showError);
      return;
    }

    const card = event.target.closest("[data-exam-code]");
    if (!card) {
      return;
    }
    selectExam(card.dataset.examCode).catch(showError);
  });

  dom.questionBuilder.addEventListener("input", (event) => {
    const target = event.target;
    const questionIndex = Number(target.dataset.questionIndex);
    if (!Number.isFinite(questionIndex) || !state.form.questions[questionIndex]) {
      return;
    }

    const question = state.form.questions[questionIndex];
    if (target.dataset.field) {
      const field = target.dataset.field;
      question[field] = field === "weight" || field === "canonical_no" ? Number(target.value || 0) : target.value;
      renderAnswerKeyStatus();
      renderActionStates();
      return;
    }

    if (target.dataset.booklet && target.dataset.mapField) {
      question.booklet_mappings[target.dataset.booklet][target.dataset.mapField] =
        target.dataset.mapField === "position" ? Number(target.value || 0) : normalizeToken(target.value);
      renderAnswerKeyStatus();
      renderActionStates();
    }
  });

  dom.questionBuilder.addEventListener("click", (event) => {
    const removeButton = event.target.closest(".remove-question-btn");
    if (!removeButton) {
      return;
    }

    const questionIndex = Number(removeButton.dataset.questionIndex);
    state.form.questions.splice(questionIndex, 1);
    renderQuestionBuilder();
    renderAnswerKeyStatus();
    renderImportHint();
    renderActionStates();
  });

  [
    [dom.examCodeInput, "exam_code"],
    [dom.examTitleInput, "title"],
    [dom.examYearInput, "exam_year"],
    [dom.examTermInput, "exam_term"],
    [dom.examTypeInput, "exam_type"],
    [dom.examDescriptionInput, "description"],
  ].forEach(([element, key]) => {
    element.addEventListener("input", () => {
      state.form[key] = element.value;
      if (key === "exam_code") {
        dom.operatorExamCodeInput.value = normalizeToken(element.value);
      }
      renderActionStates();
    });
  });
}

function showError(error) {
  const message = error?.message || "Beklenmeyen hata";
  setStatus(message, "warn");
  setCaptureStatus(message, "warn");
  setFeedback(message, "warn");
  window.alert(message);
  renderActionStates();
}

async function bootstrap() {
  state.capture.idleMs = Number(dom.captureIdleMsInput.value || 900);
  state.capture.autoArm = dom.autoArmCaptureCheckbox.checked;
  state.capture.keepBuffer = dom.keepCaptureBufferCheckbox.checked;
  renderNetRuleSelect();

  bindEvents();
  await Promise.all([loadFormTemplates(), loadExamLibrary()]);
  if (state.exams.length) {
    await selectExam(state.exams[0].exam_code);
  } else {
    fillForm(null);
  }
  renderCaptureStats();
  disarmCaptureMode("Hazır");
  renderActionStates();
}

bootstrap().catch(showError);
