/*******************************************************************************

    FUNCTIONS FOR RENDERING CHARTS AND FETCHING TAB DATA.

*******************************************************************************/

const charts = {}; // Global variable for caching parsed chart json data

NARROW_TABLE_SELECTORS = [
    '.table-narrow',
    '.table-narrow thead',
    '.table-narrow thead th',
    '.table-narrow thead div',
    '.table-narrow tbody tr th',
    '.table-narrow thead the:first-child',
    '.table-narrow tbody td',
    '.table-narrow .total-header',
]

function handleTabLoad(targetTab, forceDataReload = false) {
    if (targetTab.searchActive) {
        return;
    }
    const fetchUrl = targetTab.getAttribute('data-tab-content-url');

    const tabContent = document.querySelector(targetTab.getAttribute('href'))

    const tabChartIds = Array.from(tabContent.querySelectorAll('.chart-container')).map(el => el.id);

    if (!forceDataReload) {
        tabChartIds.forEach(chartId => {
            assignChartJson(chartId);
        });
    }

    fetchData = fetchUrl !== null && (forceDataReload || tabChartIds.length === 0);

    if (fetchData) {
        handleTabFetching(targetTab, tabChartIds);
    } else {
        targetTab.rendered = true;
        waitAndRenderCharts(targetTab, tabChartIds);
    }
}

function handleTabFetching(targetTab, tabChartIds) {
    targetTab.searchActive = true;
    targetTab.searchFailed = false;

    tabChartIds.forEach(chartId => {  // Clear chart data
        charts[chartId] = undefined;
    });

    const tabContent = document.querySelector(targetTab.getAttribute('href'));
    const dataReloadButton = tabContent.querySelector('.tab-reload-btn');
    const chartTabContent = tabContent.querySelector('.chart-tab-content');

    dataReloadButton.classList.add('disabled');

    // set the tab icon to loading.
    setTabLoading(targetTab);

    fetch(targetTab.getAttribute('data-tab-content-url'), {
        headers: {
            'Accept': 'text/html'
        }
    }).then(async response => {
        chartTabContent.innerHTML = await response.text();

        if (!response.ok) {
            setTabError(targetTab);
            return;
        }

        const newChartIds = Array.from(chartTabContent.querySelectorAll('.chart-container')).map(el => el.id);

        newChartIds.forEach(chartId => {
            assignChartJson(chartId);
        });

        waitAndRenderCharts(targetTab, newChartIds);

        targetTab.rendered = true;
        targetTab.searchActive = false;
        setTabLoaded(targetTab);
    }).catch(error => {
        console.error(error);
        showError(targetTab, chartTabContent);
    }).finally(() => {
        targetTab.searchActive = false;
        dataReloadButton.classList.remove('disabled');
    });
}

function assignChartJson(chartId) {
    chartDataScript = document.querySelector(`#${chartId}_row .chart-data`);
    if (chartDataScript) {
        // Assign chart json data stored in obtained <script> elements to appropriate place
        charts[chartId] = JSON.parse(chartDataScript.textContent);
    }
}

function waitForPaint() {
    // This method of yielding to the browser renderer works only semi-reliably,
    // but all the other methods I found, reliably didn't work.
    return new Promise((resolve) => {
        setTimeout(resolve, 250);
    });
}

function showError(targetTab, tabContent) {
    targetTab.searchFailed = true;
    tabContent.innerHTML = `
        <div class="alert alert-danger">
            <b class="alert-heading fw-bold">
                ${tabContent.getAttribute('data-text-error-occurred')}
            </b>
        </div>
    `;
    setTabError(targetTab);
}

function setTabLoading(tab) {
    tab.querySelector('.tab-tag').innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        <span class="visually-hidden">Loading...</span>
    `;
}

function setTabError(tab) {
    tab.querySelector('.tab-tag').innerHTML = `
        <i class="fas fa-fw fa-exclamation-triangle text-danger" aria-hidden="true"></i>
    `;
}

function setTabDefault(tab) {
    tab.querySelector('.tab-tag').innerHTML = '#';
}

function setTabLoaded(tab) {
    tab.querySelector('.tab-tag').innerHTML = `
        <i class="fas fa-fw fa-check text-success" aria-hidden="true"></i>
    `;
}

function addDownloadLinks(chartId, chartElem) {
    addHTMLDownloadLink(chartId, chartElem);
    addSVGDownloadLink(chartId, chartElem);
    addJSONDownloadLink(chartId);
    addCSVDownloadLink(chartId);
}

function downloadDataAsFile(dataUrl, filename) {
    const downloadLink = document.createElement('a');
    downloadLink.href = dataUrl;
    downloadLink.download = filename;
    downloadLink.click();
}

function getMatchingCSSRules(selectors) {
  let styles = "";
  const sheets = document.styleSheets;
  [...document.styleSheets].forEach(sheet => {
    [...sheet.cssRules].forEach(rule => {
        if (!rule.selectorText) return;
        const ruleSelectors = rule.selectorText.split(',').map(s => s.trim());
        selectors.forEach(sel => {
            if (ruleSelectors.includes(sel)) {
                styles += `${sel} { ${rule.style.cssText} }\n`;
            }
        });
    });
  });
  return styles;
}

function includeStylesHtmlTable(elem) {
    return `
        <style>
            .table-narrow {
                font-family: ${getComputedStyle(elem).fontFamily};
            }
            ${getMatchingCSSRules(NARROW_TABLE_SELECTORS)}
        </style>
        ${elem.outerHTML}
    `;
}

function addHTMLDownloadLink(chartId, chartElem) {
    document.getElementById(`${chartId}_export_html`)?.addEventListener('click', () => {
        let styled = '';
        if (chartElem.dataset.renderer == 'html_table') {
            styled = includeStylesHtmlTable(chartElem);
        } else {
            styled = elem.outerHTML;
        }
        const blob = new Blob([styled], {type: 'text/html'});
        const dataUrl = window.URL.createObjectURL(blob);
        downloadDataAsFile(dataUrl, `${chartId}_export.html`);
    });
}

function addSVGDownloadLink(chartId, chartElem) {
    document.getElementById(`${chartId}_export_svg`)?.addEventListener('click', () => {
        if (chartElem.dataset.renderer == 'plotly') {
            const legendStatus = chartElem.layout.showlegend;
            Plotly.relayout(chartElem, {showlegend: true}); // Show legend for export

            Plotly.toImage(chartElem, {
                format: 'svg',
                height: chartElem.offsetHeight,
                width: chartElem.offsetWidth
            }).then((dataUrl) => {
                const filename = `${chartId}_export.svg`;
                downloadDataAsFile(dataUrl, filename);
            }).finally(() => {
                Plotly.relayout(chartElem, {showlegend: legendStatus}); // Restore legend
            });
        }
    });
}

function addJSONDownloadLink(chartId) {
    document.getElementById(`${chartId}_export_json`).addEventListener('click', () => {
        const jsonDataScript = document.querySelector(`#${chartId}_row .json-data`);
        const blob = new Blob([jsonDataScript.textContent], {type: 'application/json'});
        const dataUrl = window.URL.createObjectURL(blob);
        const filename = `${chartId}_export.json`;
        downloadDataAsFile(dataUrl, filename);
    });
}

function getCSVFromJSON(jsonData) {
    if (jsonData.length === 0) {
        return '';
    }

    const columnDelimiter = ',';
    const lineDelimiter = '\n';

    const keys = Object.keys(jsonData[0]);
    const csvHeader = keys.join(columnDelimiter);
    const csvData = jsonData
        .map(row => keys.map(key => row[key]).join(columnDelimiter))
        .join(lineDelimiter);

    return `${csvHeader}${lineDelimiter}${csvData}`;
}

function addCSVDownloadLink(chartId) {
    document.getElementById(`${chartId}_export_csv`).addEventListener('click', () => {
        const jsonDataScript = document.querySelector(`#${chartId}_row .json-data`);
        const jsonData = JSON.parse(jsonDataScript.textContent);
        const csvData = getCSVFromJSON(jsonData);
        const blob = new Blob([csvData], {type: 'text/csv'});
        const dataUrl = window.URL.createObjectURL(blob);
        const filename = `${chartId}_export.csv`;
        downloadDataAsFile(dataUrl, filename);
    });
}

function renderCharts(chartIds) {
    chartIds.forEach(chartId => {
        const chartElem = document.getElementById(chartId);
        if (chartElem.dataset.renderer == 'plotly' && charts[chartId] !== undefined) {
            Plotly.react(chartElem, charts[chartId]).then(() => {
                const loadingElem = Array.from(chartElem.getElementsByClassName('loading'));
                loadingElem.forEach(le => {
                    chartElem.removeChild(le);
                });
            });
        } else if (chartElem.dataset.renderer == 'html_table') {
            // Rendered on the server-side.
        }
        addDownloadLinks(chartId, chartElem);
    });
}

// Only render charts when the tab is active
function waitAndRenderCharts(tab, tabChartIds) {
    if (tab.classList.contains('active')) {
        renderCharts(tabChartIds);
    } else {
        tab.addEventListener('shown.bs.tab', () => {
            waitForPaint().then(() => {
                renderCharts(tabChartIds);
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Set up the narrow tables to have equal column widths
    document.querySelectorAll('.table-narrow').forEach(
        table => {
            const columnHeaders = Array(...table.querySelectorAll('thead th:not(:first-child)'));
            const maxWidth = Math.max(...columnHeaders.map(th => th.offsetWidth));
            columnHeaders.forEach(th => {
                th.style.width = `${maxWidth}px`;
            });
        }
    );

    const alwaysVisibleChartIds = Array.from(document.querySelectorAll('.chart-container.always-visible')).map(chartContainer => chartContainer.id);
    alwaysVisibleChartIds.forEach(chartId => {
        assignChartJson(chartId);
    });
    renderCharts(alwaysVisibleChartIds);

    // Select all active tabs, which are not ancestors of other, non-active tabs. (i.e., They are visible at page load)
    const visibleTabs = document.querySelectorAll('a.chart-tab.active:not(.tab-pane:not(.active) a.chart-tab.active)')
    visibleTabs.forEach(handleTabLoad);

    // If there are any non-active tabs of tabs, set up event listeners to render any ancestors which should be active.
    document.querySelectorAll('a.super-chart-tab:not(.active)').forEach(scht => {
        const targetSupertab = document.querySelector(scht.getAttribute('href'));
        scht.addEventListener('shown.bs.tab', () => {
            const activeSubtabs = targetSupertab.querySelectorAll('a.chart-tab.active');
            activeSubtabs.forEach(handleTabLoad);
        });
    });

    // Add event listeners for the rest of the tabs.
    document.querySelectorAll('a.chart-tab').forEach(
        cht => cht.addEventListener('show.bs.tab', (event) => {
            if (event.target.rendered || event.target.searchFailed) {
                return;
            }
            handleTabLoad(event.target);
        })
    );

    // In case there are reload buttons, set up event listeners for them.
    document.querySelectorAll('.tab-reload-btn').forEach(
        trb => trb.addEventListener('click', (event) => {
            const targetTabId = event.currentTarget.getAttribute('data-target-tab-id');
            const targetTab = document.getElementById(targetTabId);
            handleTabLoad(targetTab, true);
        })
    );
});
