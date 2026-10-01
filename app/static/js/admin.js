// ==========================================
// GEARVN ADMIN DASHBOARD & ML/RAG SCRIPTS
// ==========================================

const Admin = {
    salesChart: null,
    forecastChart: null,
    sentimentChart: null,

    async initDashboard() {
        try {
            const token = localStorage.getItem("gearvn_token");
            const headers = token ? { "Authorization": `Bearer ${token}` } : {};

            const res = await fetch("/api/v1/analytics/realtime", { headers });
            const data = await res.json();

            // Populate cards
            document.getElementById("statTodayRevenue").innerText = `${data.today_revenue.toLocaleString()} đ`;
            document.getElementById("statTodayOrders").innerText = data.today_orders;
            document.getElementById("statTotalProducts").innerText = data.total_products;
            document.getElementById("statTotalCustomers").innerText = data.total_customers;

            // Render Top Selling
            const topList = document.getElementById("topSellingList");
            if (topList) {
                topList.innerHTML = data.top_selling_products.map(p => `
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <img src="${p.thumbnail || 'https://via.placeholder.com/40'}" style="width:36px;height:36px;object-fit:cover;border-radius:4px;">
                            <div>
                                <div style="font-size:13px;font-weight:600;max-width:240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.name}</div>
                                <div style="font-size:11px;color:#6b7280;">Đã bán: ${p.sales_count} chiếc</div>
                            </div>
                        </div>
                        <div style="font-weight:700;font-size:13px;color:#e30019;">${p.revenue.toLocaleString()} đ</div>
                    </div>
                `).join("");
            }

            // Render Sentiment Chart
            this.renderSentimentChart(data.sentiment_summary);

            // Load & Render ML Forecast
            this.loadSalesForecast();

        } catch (err) {
            console.error("Dashboard init error:", err);
        }
    },

    renderSentimentChart(sentimentData) {
        const ctx = document.getElementById("sentimentChartCanvas")?.getContext("2d");
        if (!ctx) return;

        if (this.sentimentChart) this.sentimentChart.destroy();

        this.sentimentChart = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Tích cực (Positive)", "Trung tính (Neutral)", "Tiêu cực (Negative)"],
                datasets: [{
                    data: [sentimentData.positive_count, sentimentData.neutral_count, sentimentData.negative_count],
                    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom" }
                }
            }
        });
    },

    async loadSalesForecast() {
        try {
            const token = localStorage.getItem("gearvn_token");
            const headers = token ? { "Authorization": `Bearer ${token}` } : {};

            const res = await fetch("/api/v1/analytics/forecast?hours=12", { headers });
            const data = await res.json();

            document.getElementById("mlModelName").innerText = data.model_name;
            document.getElementById("mlR2Score").innerText = `R² = ${data.r2_score}`;
            document.getElementById("mlInsightText").innerText = data.summary_insight;

            const ctx = document.getElementById("salesForecastChartCanvas")?.getContext("2d");
            if (!ctx) return;

            const histLabels = data.historical_revenue.map(p => p.time_label);
            const histValues = data.historical_revenue.map(p => p.revenue);

            const foreLabels = data.forecast.map(p => p.time_label);
            const foreValues = data.forecast.map(p => p.predicted_revenue);
            const foreUpper = data.forecast.map(p => p.upper_bound);
            const foreLower = data.forecast.map(p => p.lower_bound);

            const allLabels = [...histLabels, ...foreLabels];
            const alignedHist = [...histValues, ...Array(foreLabels.length).fill(null)];
            const alignedFore = [...Array(histLabels.length - 1).fill(null), histValues[histValues.length - 1], ...foreValues];

            if (this.forecastChart) this.forecastChart.destroy();

            this.forecastChart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: allLabels,
                    datasets: [
                        {
                            label: "Doanh số thực tế (CSV History)",
                            data: alignedHist,
                            borderColor: "#2563eb",
                            backgroundColor: "rgba(37, 99, 235, 0.1)",
                            tension: 0.3,
                            fill: true
                        },
                        {
                            label: "Dự báo ML (Forecast)",
                            data: alignedFore,
                            borderColor: "#e30019",
                            borderDash: [5, 5],
                            backgroundColor: "rgba(227, 0, 25, 0.05)",
                            tension: 0.3,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            ticks: {
                                callback: val => `${(val / 1000000).toFixed(0)}Tr`
                            }
                        }
                    }
                }
            });

        } catch (e) {
            console.error("Forecast load error:", e);
        }
    },

    // Internal Knowledge Base Tra Cuu Quy Dinh
    async askRAG() {
        const input = document.getElementById("ragQuestionInput");
        const answerBox = document.getElementById("ragAnswerBox");
        const citationsBox = document.getElementById("ragCitationsBox");
        const spaceSelect = document.getElementById("ragQuerySpace");
        if (!input || !answerBox) return;

        const query = input.value.trim();
        if (!query) return;

        const spaceCategory = spaceSelect ? spaceSelect.value : null;

        answerBox.innerHTML = `<div style="display:flex;align-items:center;gap:8px;color:#64748b;"><i class="fa-solid fa-spinner fa-spin"></i> <span>Đang đối soát quy định trong danh mục [${spaceCategory === 'all' || !spaceCategory ? 'Tất cả quy định' : spaceCategory}]...</span></div>`;
        if (citationsBox) citationsBox.innerHTML = "";

        try {
            const token = localStorage.getItem("gearvn_token");
            const headers = { "Content-Type": "application/json" };
            if (token) headers["Authorization"] = `Bearer ${token}`;

            const res = await fetch("/api/v1/rag/query", {
                method: "POST",
                headers: headers,
                body: JSON.stringify({
                    query: query,
                    space_category: spaceCategory && spaceCategory !== 'all' ? spaceCategory : null,
                    top_k: 1
                })
            });

            const data = await res.json();
            
            let badgeHtml = `<div style="display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;background:#f3e8ff;color:#9333ea;margin-bottom:8px;"><i class="fa-solid fa-folder-open"></i> Danh mục: ${data.vector_space_used}</div>`;
            answerBox.innerHTML = badgeHtml + "<div style='margin-top:4px;font-size:13.5px;color:#1e293b;line-height:1.6;'>" + data.answer.replace(/\n/g, "<br>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") + "</div>";

            if (citationsBox && data.citations && data.citations.length > 0) {
                const c = data.citations[0];
                citationsBox.innerHTML = `
                    <div style="font-weight:700;font-size:12px;margin-top:14px;color:#475569;border-top:1px solid #e2e8f0;padding-top:10px;">
                        <i class="fa-solid fa-file-contract" style="color:#9333ea;"></i> Đoạn trích dẫn quy định gốc có độ phù hợp cao nhất:
                    </div>
                    <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:12px;border-radius:6px;margin-top:8px;font-size:12.5px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <strong style="color:#0f172a;">📄 ${c.title}</strong>
                            <span style="background:#dcfce7;color:#15803d;font-weight:700;padding:2px 8px;border-radius:4px;font-size:11px;">
                                <i class="fa-solid fa-circle-check"></i> Độ chính xác: ${(c.score * 100).toFixed(1)}%
                            </span>
                        </div>
                        <div style="color:#64748b;font-size:11px;margin-bottom:6px;">Phân nhóm: <span style="color:#2563eb;font-weight:600;">${c.category}</span></div>
                        <div style="color:#334155;background:#fff;padding:8px 10px;border-radius:4px;border-left:3px solid #9333ea;line-height:1.5;">"${c.snippet}"</div>
                    </div>
                `;
            }

        } catch (err) {
            console.error("Query Error:", err);
            answerBox.innerHTML = `<span style="color:red;"><i class="fa-solid fa-triangle-exclamation"></i> Không thể kết nối tới máy chủ tra cứu.</span>`;
        }
    }
};
