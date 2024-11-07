import "../index.css";
import { useState } from "react";

export default function Home() {
    const [url, setUrl] = useState("");
    const [fileUrl, setFileUrl] = useState(""); // State to store the file download URL

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch("http://127.0.0.1:8000/scrape", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ url }),
            });

            if (response.ok) {
                // Blob response to handle file download
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                
                // Set the file URL in state
                setFileUrl(downloadUrl);

                console.log("File ready for download");
            } else {
                console.error("Failed to fetch file");
            }
        } catch (error) {
            console.error("Error fetching file:", error);
        }
    };

    const handleDownload = () => {
        if (fileUrl) {
            const link = document.createElement("a");
            link.href = fileUrl;
            link.download = "scraped_data.xlsx";  // Set the filename
            document.body.appendChild(link);
            link.click();

            // Clean up
            link.remove();
            window.URL.revokeObjectURL(fileUrl);
            setFileUrl(""); // Reset the file URL state after download
        }
    };

    return (
        <div className="BG">
            <div className="content">
                <h1>Scrap It</h1>
                <h2>The app helps with Amazon Product Detail scraping</h2>
                <p>
                    <strong>"Scrap It"</strong> is a tool to help you extract details about Amazon products using a provided product link.
                </p>
            </div>

            <div className="project">
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Enter URL..."
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                    />
                    <button className ="button" type="submit">Submit</button>
                </form>
                {/* Show download button only when fileUrl is set */}
                {fileUrl && (
                    <button  className= "btn" onClick={handleDownload}>
                        Download Scraped Data
                    </button>
                )}
            </div>
        </div>
    );
}
