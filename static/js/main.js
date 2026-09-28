/**
 * PlacePredict AI - Frontend Logic & Dynamic Reactivity
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('predictionForm');
    const cgpaInput = document.getElementById('cgpaInput');
    const cgpaVal = document.getElementById('cgpaVal');
    const sscInput = document.getElementById('sscInput');
    const sscVal = document.getElementById('sscVal');
    const hscInput = document.getElementById('hscInput');
    const hscVal = document.getElementById('hscVal');
    const aptitudeInput = document.getElementById('aptitudeInput');
    const aptitudeVal = document.getElementById('aptitudeVal');
    const softSkillsInput = document.getElementById('softSkillsInput');
    const softSkillsVal = document.getElementById('softSkillsVal');
    
    const projectsInput = document.getElementById('projectsInput');
    const internshipsInput = document.getElementById('internshipsInput');
    const workshopsInput = document.getElementById('workshopsInput');
    
    const placementTrainingToggle = document.getElementById('placementTrainingToggle');
    const extracurricularToggle = document.getElementById('extracurricularToggle');
    
    const runPredictionBtn = document.getElementById('runPredictionBtn');
    const resetDefaultsBtn = document.getElementById('resetDefaultsBtn');
    
    // Result Elements
    const probPercent = document.getElementById('probPercent');
    const gaugeFillCircle = document.getElementById('gaugeFillCircle');
    const verdictBadge = document.getElementById('verdictBadge');
    const verdictIcon = document.getElementById('verdictIcon');
    const verdictText = document.getElementById('verdictText');
    const verdictSummary = document.getElementById('verdictSummary');
    const consensusBarFill = document.getElementById('consensusBarFill');
    const consensusVal = document.getElementById('consensusVal');
    const modelsGrid = document.getElementById('modelsGrid');
    const recommendationsList = document.getElementById('recommendationsList');
    
    // Preset archetypes
    const PRESETS = {
        top: {
            cgpa: 9.2,
            aptitude: 92,
            ssc_marks: 88,
            hsc_marks: 90,
            projects: 3,
            internships: 2,
            workshops: 2,
            soft_skills: 4.8,
            placement_training: true,
            extracurricular: true
        },
        balanced: {
            cgpa: 8.0,
            aptitude: 82,
            ssc_marks: 75,
            hsc_marks: 78,
            projects: 2,
            internships: 1,
            workshops: 1,
            soft_skills: 4.5,
            placement_training: true,
            extracurricular: true
        },
        borderline: {
            cgpa: 7.1,
            aptitude: 70,
            ssc_marks: 65,
            hsc_marks: 68,
            projects: 1,
            internships: 0,
            workshops: 1,
            soft_skills: 3.8,
            placement_training: true,
            extracurricular: false
        },
        atrisk: {
            cgpa: 6.2,
            aptitude: 58,
            ssc_marks: 55,
            hsc_marks: 60,
            projects: 0,
            internships: 0,
            workshops: 0,
            soft_skills: 3.2,
            placement_training: false,
            extracurricular: false
        }
    };

    // Sync input displays
    function syncValueBadges() {
        cgpaVal.textContent = parseFloat(cgpaInput.value).toFixed(1);
        sscVal.textContent = `${sscInput.value}%`;
        hscVal.textContent = `${hscInput.value}%`;
        aptitudeVal.textContent = aptitudeInput.value;
        softSkillsVal.textContent = `${parseFloat(softSkillsInput.value).toFixed(1)} / 5.0`;
    }

    // Stepper logic (+ / -)
    document.querySelectorAll('.step-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const field = btn.getAttribute('data-step');
            const dir = parseInt(btn.getAttribute('data-dir'), 10);
            const input = document.getElementById(`${field}Input`);
            if (input) {
                let current = parseInt(input.value, 10) || 0;
                let min = parseInt(input.min, 10) || 0;
                let max = parseInt(input.max, 10) || 10;
                let next = current + dir;
                if (next >= min && next <= max) {
                    input.value = next;
                    triggerPredictionDebounced();
                }
            }
        });
    });

    // Preset selection
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const presetKey = btn.getAttribute('data-preset');
            const data = PRESETS[presetKey];
            if (data) {
                applyPreset(data);
            }
        });
    });

    function applyPreset(data) {
        cgpaInput.value = data.cgpa;
        aptitudeInput.value = data.aptitude;
        sscInput.value = data.ssc_marks;
        hscInput.value = data.hsc_marks;
        projectsInput.value = data.projects;
        internshipsInput.value = data.internships;
        workshopsInput.value = data.workshops;
        softSkillsInput.value = data.soft_skills;
        placementTrainingToggle.checked = data.placement_training;
        extracurricularToggle.checked = data.extracurricular;
        
        syncValueBadges();
        triggerPrediction();
    }

    // Collect Form Payload
    function getFormData() {
        return {
            cgpa: parseFloat(cgpaInput.value),
            aptitude: parseFloat(aptitudeInput.value),
            ssc_marks: parseFloat(sscInput.value),
            hsc_marks: parseFloat(hscInput.value),
            projects: parseInt(projectsInput.value, 10),
            internships: parseInt(internshipsInput.value, 10),
            workshops: parseInt(workshopsInput.value, 10),
            soft_skills: parseFloat(softSkillsInput.value),
            placement_training: placementTrainingToggle.checked ? 1 : 0,
            extracurricular: extracurricularToggle.checked ? 1 : 0
        };
    }

    // Animate Gauge & Verdict
    function updateVerdictUI(data) {
        const prob = data.probability;
        const isPlaced = data.prediction === 1;

        // Animate counter
        probPercent.textContent = `${prob.toFixed(1)}%`;
        
        // Circular gauge dashoffset: circumference = 2 * PI * 50 = ~314.16
        const circumference = 314.16;
        const offset = circumference - (prob / 100) * circumference;
        gaugeFillCircle.style.strokeDashoffset = offset;
        
        if (isPlaced) {
            gaugeFillCircle.style.stroke = 'var(--accent-emerald)';
            verdictBadge.className = 'verdict-badge placed';
            verdictIcon.textContent = '✓';
            verdictText.textContent = 'LIKELY PLACED';
            verdictSummary.textContent = `High employability profile. The champion ${data.champion_model} model projects a ${prob.toFixed(1)}% probability of securing campus placement.`;
        } else {
            gaugeFillCircle.style.stroke = 'var(--accent-rose)';
            verdictBadge.className = 'verdict-badge not-placed';
            verdictIcon.textContent = '✕';
            verdictText.textContent = 'AT RISK (NOT PLACED)';
            verdictSummary.textContent = `Current metrics fall below historical placement thresholds. Targeted interventions recommended to boost employability.`;
        }

        // Consensus Bar
        consensusBarFill.style.width = `${data.consensus_rate}%`;
        const agreeCount = Math.round((data.consensus_rate / 100) * Object.keys(data.all_models).length);
        consensusVal.textContent = `${agreeCount} / ${Object.keys(data.all_models).length} Models Agree`;

        // Render Multi-Model Grid
        renderModelsGrid(data.all_models);

        // Render Recommendations
        renderRecommendations(data.recommendations);
    }

    function renderModelsGrid(models) {
        modelsGrid.innerHTML = '';
        
        for (const [name, info] of Object.entries(models)) {
            const isPlaced = info.prediction === 1;
            const card = document.createElement('div');
            card.className = 'model-row-card';
            
            const probVal = info.probability !== null ? `${info.probability.toFixed(1)}%` : '--';
            const barWidth = info.probability !== null ? `${info.probability}%` : (isPlaced ? '100%' : '0%');
            const barColor = isPlaced ? 'var(--accent-emerald)' : 'var(--accent-rose)';

            card.innerHTML = `
                <div class="model-info-col">
                    <span class="model-name-text">${name}</span>
                    <span class="model-acc-tag">Benchmark Acc: ${info.accuracy}%</span>
                </div>
                <div class="model-prediction-col">
                    <div class="prob-bar-mini" title="Probability: ${probVal}">
                        <div class="prob-bar-fill-mini" style="width: ${barWidth}; background: ${barColor};"></div>
                    </div>
                    <span class="status-pill ${isPlaced ? 'placed' : 'not-placed'}">
                        ${info.status} (${probVal})
                    </span>
                </div>
            `;
            modelsGrid.appendChild(card);
        }
    }

    function renderRecommendations(recommendations) {
        recommendationsList.innerHTML = '';
        if (!recommendations || recommendations.length === 0) {
            recommendationsList.innerHTML = '<li>Profile meets all benchmark criteria. Excellent readiness!</li>';
            return;
        }

        recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recommendationsList.appendChild(li);
        });
    }

    // Call API
    let isFetching = false;
    async function triggerPrediction() {
        if (isFetching) return;
        isFetching = true;
        
        try {
            const payload = getFormData();
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                updateVerdictUI(data);
            }
        } catch (err) {
            console.error('Prediction request error:', err);
        } finally {
            isFetching = false;
        }
    }

    // Debounce helper for smooth slider interaction
    let debounceTimer = null;
    function triggerPredictionDebounced() {
        syncValueBadges();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            triggerPrediction();
        }, 120);
    }

    // Event Listeners for Sliders & Toggles
    [cgpaInput, sscInput, hscInput, aptitudeInput, softSkillsInput].forEach(slider => {
        slider.addEventListener('input', triggerPredictionDebounced);
    });

    [placementTrainingToggle, extracurricularToggle].forEach(toggle => {
        toggle.addEventListener('change', triggerPredictionDebounced);
    });

    runPredictionBtn.addEventListener('click', triggerPrediction);

    resetDefaultsBtn.addEventListener('click', () => {
        document.getElementById('presetBalancedBtn').click();
    });

    // Initial Trigger
    syncValueBadges();
    triggerPrediction();
});
