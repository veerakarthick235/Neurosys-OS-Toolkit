import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;

public class EcommerceTestPlan {
    public static void main(String[] args) {

        System.setProperty("webdriver.chrome.driver", "chromedriver.exe");
        WebDriver driver = new ChromeDriver();

        // Open application
        driver.get("https://example-ecommerce.com");

        // Login
        driver.findElement(By.id("username")).sendKeys("user");
        driver.findElement(By.id("password")).sendKeys("1234");
        driver.findElement(By.id("login")).click();

        // Search product
        driver.findElement(By.id("search")).sendKeys("Laptop");
        driver.findElement(By.id("searchBtn")).click();

        // Add to cart
        driver.findElement(By.id("product1")).click();
        driver.findElement(By.id("addToCart")).click();

        driver.quit();
    }
}



📊 Output
Application opens in browser
User login is performed
Product search results are displayed
Product is added to cart successfully
