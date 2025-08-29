/**
 * @file Manages all frontend interactivity for the Blindspot AI Sandbox dashboard.
 * - Handles the manual prompt analysis form.
 * - Builds the detailed, multi-card insight report after a scan.
 * - Periodically refreshes the "Recent Scans" log.
 */

document.addEventListener('DOMContentLoaded', function() {
    // --- DOM Element Selectors ---
    const manualScanBtn = document.getElementById('manual-scan-btn');
    const manualInput = document.getElementById('manual-prompt-input');
    const resultsContainer = document.getElementById('scan-results-container');
    const eventsTableBody = document.getElementById('events-table-body');
    let riskChart = null; // Holds the Chart.js instance

    /**
     * Handles the click event for the main "Analyze Prompt" button.
     */
    if (manualScanBtn) {
        manualScanBtn.addEventListener('click', async () => {
            const promptText = manualInput.value;
            if (!promptText.trim()) {
                alert('Please enter a prompt to analyze.');
                return;
            }

            // Update UI to show loading state
            manualScanBtn.disabled = true;
            manualScanBtn.textContent = 'Analyzing...';
            resultsContainer.innerHTML = '<p style="text-align: center;">Analyzing prompt, please wait...</p>';

            try {
                // Send the prompt to the backend API for analysis
                const body = new URLSearchParams({ input_text: promptText });
                const response = await fetch('/api/scan/text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: body
                });

                if (!response.ok) {
                    throw new Error(`HTTP Error: ${response.status}`);
                }
                const result = await response.json();

                // Build the visual report and update the events log
                buildInsightReport(result);
                updateRecentEvents();

            } catch (error) {
                resultsContainer.innerHTML = `<p style="color: #ff6b6b; text-align: center;">Error: Analysis failed. ${error.message}</p>`;
                console.error('Manual Scan Error:', error);
            }

            // Restore the UI after the scan is complete
            manualScanBtn.disabled = false;
            manualScanBtn.textContent = 'Analyze Prompt';
        });
    }

    /**
     * Takes the full analysis result from the API and builds the multi-card
     * visual report in the DOM.
     * @param {object} scanResult The JSON response from the /api/scan/text endpoint.
     */
    const buildInsightReport = (scanResult) => {
        resultsContainer.innerHTML = ''; // Clear previous results

        // 1. Create and append the Overall Risk Score card (Chart)
        const chartCard = document.createElement('div');
        chartCard.className = 'chart-card';
        chartCard.innerHTML = `<h3>Overall Risk Score</h3><div class="chart-container"><canvas id="risk-score-chart"></canvas></div>`;
        resultsContainer.appendChild(chartCard);

        // 2. Create and append the Prompt Metadata card
        const metadataCard = document.createElement('div');
        metadataCard.className = 'metadata-card';
        const analytics = scanResult.analytics || {};
        const attackType = analytics.attack_type || 'N/A';
        metadataCard.innerHTML = `
            <h3>Prompt Metadata</h3>
            <div class="metadata-item"><span class="metadata-label">Attack Type</span><span class="metadata-value attack-type">${attackType}</span></div>
            <div class="metadata-item"><span class="metadata-label">Language</span><span class="metadata-value">${analytics.language || 'N/A'}</span></div>
            <div class="metadata-item"><span class="metadata-label">Character Count</span><span class="metadata-value">${analytics.char_count || 0}</span></div>
            <div class="metadata-item"><span class="metadata-label">Token Count</span><span class="metadata-value">${analytics.token_count || 0}</span></div>
        `;
        resultsContainer.appendChild(metadataCard);

        // 3. Create and append the Detailed Findings card
        const findingsCard = document.createElement('div');
        findingsCard.className = 'findings-card';
        let findingsHTML = '<h3>Detailed Findings</h3>';
        if (scanResult.findings && scanResult.findings.length > 0) {
            findingsHTML += '<ul class="findings-list">';
            scanResult.findings.forEach(finding => {
                let cardClass = '';
                if (finding.finding.includes('PII')) cardClass = 'pii';
                if (finding.finding.includes('Language')) cardClass = 'language';
                if (finding.finding.includes('Contextual')) cardClass = 'contextual';
                findingsHTML += `
                    <li class="finding-item ${cardClass}">
                        <p class="finding-title">${finding.finding}</p>
                        <p>${finding.details}</p>
                        <div class="mitigation">
                            <strong>Mitigation:</strong> ${finding.mitigation || 'Standard monitoring practices are advised.'}
                        </div>
                    </li>`;
            });
            findingsHTML += '</ul>';
        } else {
            findingsHTML += `<p>No specific threats were found. The risk score of ${scanResult.prompt_risk.toFixed(2)} is based on overall semantic similarity.</p>`;
        }
        findingsCard.innerHTML = findingsHTML;
        resultsContainer.appendChild(findingsCard);

        // 4. Render the Chart.js doughnut chart
        const riskScore = scanResult.prompt_risk || 0;
        const ctx = document.getElementById('risk-score-chart').getContext('2d');
        if (riskChart) {
            riskChart.destroy(); // Clear previous chart instance
        }
        riskChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [riskScore, 1.0 - riskScore],
                    backgroundColor: ['#ff7f50', '#333'],
                    borderColor: '#1e1e1e',
                    borderWidth: 4,
                    circumference: 180,
                    rotation: 270,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: { legend: { display: false }, tooltip: { enabled: false } }
            }
        });
    };

    /**
     * Fetches the latest events from the API and updates the "Recent Scans" table.
     */
    const updateRecentEvents = async () => {
        try {
            const response = await fetch('/api/events');
            if (!response.ok) return;
            const events = await response.json();

            eventsTableBody.innerHTML = '';
            if (events.length === 0) {
                eventsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No scan events yet.</td></tr>';
                return;
            }

            // Display the 5 most recent events
            events.slice(0, 5).forEach(event => {
                const data = event.data;
                const prompt_risk = parseFloat(data.prompt_risk || 0);
                
                let findingsSummary = 'Benign';
                if (data.findings && data.findings.length > 0) {
                    findingsSummary = data.findings.map(finding => finding.finding).join(', ');
                } else if (data.analytics.attack_type !== 'Benign') {
                    findingsSummary = data.analytics.attack_type;
                }

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(event.timestamp).toLocaleString()}</td>
                    <td class="status-${data.status}">${data.status}</td>
                    <td>${prompt_risk.toFixed(2)}</td>
                    <td>${findingsSummary}</td>
                `;
                eventsTableBody.appendChild(row);
            });
        } catch (error) {
            console.error("Error updating recent events:", error);
            eventsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Could not load events.</td></tr>';
        }
    };
    
    // --- Initial Load and Periodic Updates ---
    updateRecentEvents();
    setInterval(updateRecentEvents, 10000); // Refresh the log every 10 seconds
});