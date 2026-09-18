from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    orders = get_orders()

    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        preview_robot()
        submit_order()

        pdf_file = store_receipt_as_pdf(order["Order number"])
        screenshot = screenshot_robot(order["Order number"])

        embed_screenshot_to_receipt(screenshot, pdf_file)
        order_another_robot()

    archive_receipts()


def open_robot_order_website():
    """Opens the RobotSpareBin Industries robot order website."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    """Downloads the orders file and returns it as a table."""
    http = HTTP()
    http.download(
        url="https://robotsparebinindustries.com/orders.csv",
        target_file="orders.csv",
        overwrite=True,
    )

    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv", header=True)

    return orders


def close_annoying_modal():
    """Closes the annoying modal."""
    page = browser.page()
    page.click("text=OK")


def fill_the_form(order):
    """Fills the robot order form."""
    page = browser.page()

    page.select_option("#head", order["Head"])
    page.check(f"#id-body-{order['Body']}")
    page.fill(
        "input[placeholder='Enter the part number for the legs']",
        order["Legs"],
    )
    page.fill("#address", order["Address"])


def preview_robot():
    """Previews the robot."""
    page = browser.page()
    page.click("#preview")


def submit_order():
    """Submits the order and retries until successful."""
    page = browser.page()

    while True:
        page.click("#order")

        if page.locator("#receipt").is_visible():
            break


def store_receipt_as_pdf(order_number):
    """Stores the order receipt as a PDF file."""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_file = f"output/receipts/receipt_{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_file)

    return pdf_file


def screenshot_robot(order_number):
    """Takes a screenshot of the ordered robot."""
    page = browser.page()
    screenshot = f"output/receipts/robot_{order_number}.png"

    page.locator("#robot-preview-image").screenshot(path=screenshot)

    return screenshot


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the robot screenshot into the receipt PDF."""
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[screenshot],
        target_document=pdf_file,
        append=True,
    )


def order_another_robot():
    """Goes to order another robot."""
    page = browser.page()
    page.click("#order-another")


def archive_receipts():
    """Creates a ZIP archive containing all receipt PDF files."""
    archive = Archive()
    archive.archive_folder_with_zip(
        folder="output/receipts",
        archive_name="output/receipts.zip",
        recursive=False,
        include="*.pdf",
    )