using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace BankBridgeClient
{
    // Models
    public class User
    {
        [JsonProperty("id")]
        public int Id { get; set; }
        
        [JsonProperty("username")]
        public string Username { get; set; } = string.Empty;
        
        [JsonProperty("email")]
        public string Email { get; set; } = string.Empty;
        
        [JsonProperty("account_number")]
        public string AccountNumber { get; set; } = string.Empty;
        
        [JsonProperty("balance")]
        public decimal Balance { get; set; }
        
        [JsonProperty("phone")]
        public string Phone { get; set; } = string.Empty;
        
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
    }

    public class ApiResponse
    {
        [JsonProperty("message")]
        public string? Message { get; set; }
        
        [JsonProperty("token")]
        public string? Token { get; set; }
        
        [JsonProperty("user")]
        public User? User { get; set; }
        
        [JsonProperty("new_balance")]
        public decimal NewBalance { get; set; }
        
        [JsonProperty("error")]
        public string? Error { get; set; }
        
        [JsonProperty("balance")]
        public decimal Balance { get; set; }
        
        [JsonProperty("account_number")]
        public string? AccountNumber { get; set; }
    }

    public class Transaction
    {
        [JsonProperty("id")]
        public int Id { get; set; }
        
        [JsonProperty("from_username")]
        public string FromUsername { get; set; } = string.Empty;
        
        [JsonProperty("to_username")]
        public string ToUsername { get; set; } = string.Empty;
        
        [JsonProperty("amount")]
        public decimal Amount { get; set; }
        
        [JsonProperty("transaction_type")]
        public string TransactionType { get; set; } = string.Empty;
        
        [JsonProperty("description")]
        public string Description { get; set; } = string.Empty;
        
        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; }
    }

    // Main Program
    class Program
    {
        private static readonly HttpClient httpClient = new HttpClient();
        private static string? authToken;
        private static User? currentUser;
        private const string BASE_URL = "http://localhost:8000/api";

        static async Task Main(string[] args)
        {
            Console.OutputEncoding = Encoding.UTF8;
            
            while (true)
            {
                if (currentUser == null)
                {
                    await ShowMainMenu();
                }
                else
                {
                    await ShowUserDashboard();
                }
            }
        }

        static async Task ShowMainMenu()
        {
            while (true)
            {
                Console.Clear();
                PrintHeader();
                Console.WriteLine("\n┌────────────────────────────────────────┐");
                Console.WriteLine("│              MAIN MENU                  │");
                Console.WriteLine("├────────────────────────────────────────┤");
                Console.WriteLine("│ 1. Login                                │");
                Console.WriteLine("│ 2. Register New Account                 │");
                Console.WriteLine("│ 3. Exit                                 │");
                Console.WriteLine("└────────────────────────────────────────┘");
                Console.Write("\nChoose an option: ");
                
                string? choice = Console.ReadLine();
                
                switch (choice)
                {
                    case "1":
                        await Login();
                        break;
                    case "2":
                        await Register();
                        break;
                    case "3":
                        Console.WriteLine("\n✨ Thank you for using BankBridge. Goodbye!");
                        Environment.Exit(0);
                        break;
                    default:
                        Console.WriteLine("\n❌ Invalid option!");
                        PressEnter();
                        break;
                }
                
                if (currentUser != null) break;
            }
        }

        static async Task ShowUserDashboard()
        {
            while (currentUser != null)
            {
                Console.Clear();
                PrintHeader();
                Console.WriteLine($"\n👋 Welcome back, {currentUser.Username}!");
                Console.WriteLine($"📁 Account: {currentUser.AccountNumber}");
                Console.WriteLine($"💰 Balance: {currentUser.Balance:C}");
                
                Console.WriteLine("\n┌────────────────────────────────────────┐");
                Console.WriteLine("│           USER DASHBOARD                │");
                Console.WriteLine("├────────────────────────────────────────┤");
                Console.WriteLine("│ 1. 👤 View Profile                      │");
                Console.WriteLine("│ 2. 💰 Check Balance                     │");
                Console.WriteLine("│ 3. 💵 Deposit Money                     │");
                Console.WriteLine("│ 4. 💸 Withdraw Money                    │");
                Console.WriteLine("│ 5. 📤 Send Money                        │");
                Console.WriteLine("│ 6. 📜 Transaction History               │");
                Console.WriteLine("│ 7. 🚪 Logout                            │");
                Console.WriteLine("└────────────────────────────────────────┘");
                Console.Write("\nChoose an option: ");
                
                string? choice = Console.ReadLine();
                
                switch (choice)
                {
                    case "1":
                        await ViewProfile();
                        break;
                    case "2":
                        await CheckBalance();
                        break;
                    case "3":
                        await Deposit();
                        break;
                    case "4":
                        await Withdraw();
                        break;
                    case "5":
                        await Transfer();
                        break;
                    case "6":
                        await ViewTransactions();
                        break;
                    case "7":
                        await Logout();
                        break;
                    default:
                        Console.WriteLine("\n❌ Invalid option!");
                        break;
                }
                
                if (currentUser != null)
                    PressEnter();
            }
        }

        static async Task Login()
        {
            try
            {
                Console.Clear();
                Console.WriteLine("\n🔐 === LOGIN ===\n");
                Console.Write("Username: ");
                string username = Console.ReadLine() ?? string.Empty;
                Console.Write("Password: ");
                string password = Console.ReadLine() ?? string.Empty;

                var loginData = new { username, password };
                string json = JsonConvert.SerializeObject(loginData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync($"{BASE_URL}/login/", content);
                string responseBody = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var apiResponse = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    if (apiResponse?.Token != null && apiResponse.User != null)
                    {
                        authToken = apiResponse.Token;
                        currentUser = apiResponse.User;
                        httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Token", authToken);
                        Console.WriteLine("\n✅ Login successful!");
                        PressEnter();
                    }
                }
                else
                {
                    Console.WriteLine("\n❌ Login failed! Invalid credentials.");
                    PressEnter();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
                Console.WriteLine("Make sure the Django server is running on http://localhost:8000");
                PressEnter();
            }
        }

        static async Task Register()
        {
            try
            {
                Console.Clear();
                Console.WriteLine("\n📝 === REGISTRATION ===\n");
                Console.Write("Username: ");
                string username = Console.ReadLine() ?? string.Empty;
                Console.Write("Email: ");
                string email = Console.ReadLine() ?? string.Empty;
                Console.Write("Password (min 6 chars): ");
                string password = Console.ReadLine() ?? string.Empty;
                Console.Write("Confirm Password: ");
                string confirmPassword = Console.ReadLine() ?? string.Empty;
                Console.Write("Phone Number: ");
                string phone = Console.ReadLine() ?? string.Empty;

                if (password != confirmPassword)
                {
                    Console.WriteLine("\n❌ Passwords do not match!");
                    PressEnter();
                    return;
                }

                var registerData = new { username, email, password, confirm_password = confirmPassword, phone };
                string json = JsonConvert.SerializeObject(registerData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync($"{BASE_URL}/register/", content);
                string responseBody = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var apiResponse = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    Console.WriteLine($"\n✅ {apiResponse?.Message ?? "Registration successful!"}");
                    Console.WriteLine("\nYou can now login with your credentials.");
                }
                else
                {
                    Console.WriteLine($"\n❌ Registration failed!");
                }
                PressEnter();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
                PressEnter();
            }
        }

        static async Task Logout()
        {
            if (authToken != null)
            {
                try
                {
                    await httpClient.PostAsync($"{BASE_URL}/logout/", null);
                }
                catch { }
                
                authToken = null;
                currentUser = null;
                httpClient.DefaultRequestHeaders.Authorization = null;
                Console.WriteLine("\n✅ Logged out successfully!");
            }
        }

        static async Task CheckBalance()
        {
            try
            {
                HttpResponseMessage response = await httpClient.GetAsync($"{BASE_URL}/balance/");
                string responseBody = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var balanceData = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    Console.WriteLine($"\n💰 Account Number: {balanceData?.AccountNumber}");
                    Console.WriteLine($"💰 Current Balance: {balanceData?.Balance:C}");
                }
                else
                {
                    Console.WriteLine("\n❌ Failed to fetch balance!");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
            }
        }

        static async Task Deposit()
        {
            try
            {
                Console.Write("\n💵 Enter amount to deposit: $");
                if (!decimal.TryParse(Console.ReadLine(), out decimal amount) || amount <= 0)
                {
                    Console.WriteLine("\n❌ Invalid amount!");
                    return;
                }

                var depositData = new { amount };
                string json = JsonConvert.SerializeObject(depositData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync($"{BASE_URL}/deposit/", content);
                string responseBody = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var result = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    Console.WriteLine($"\n✅ {result?.Message}");
                    Console.WriteLine($"💰 New Balance: {result?.NewBalance:C}");
                    
                    // Update current user balance
                    if (currentUser != null && result?.NewBalance != null)
                        currentUser.Balance = result.NewBalance;
                }
                else
                {
                    var error = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    Console.WriteLine($"\n❌ Deposit failed: {error?.Error}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
            }
        }

        static async Task Withdraw()
        {
            try
            {
                Console.Write("\n💸 Enter amount to withdraw: $");
                if (!decimal.TryParse(Console.ReadLine(), out decimal amount) || amount <= 0)
                {
                    Console.WriteLine("\n❌ Invalid amount!");
                    return;
                }

                var withdrawData = new { amount };
                string json = JsonConvert.SerializeObject(withdrawData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync($"{BASE_URL}/withdraw/", content);
                string responseBody = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var result = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    Console.WriteLine($"\n✅ {result?.Message}");
                    Console.WriteLine($"💰 New Balance: {result?.NewBalance:C}");
                    
                    // Update current user balance
                    if (currentUser != null && result?.NewBalance != null)
                        currentUser.Balance = result.NewBalance;
                }
                else
                {
                    var error = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    Console.WriteLine($"\n❌ Withdrawal failed: {error?.Error}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
            }
        }

        static async Task Transfer()
        {
            try
            {
                Console.WriteLine("\n📤 === SEND MONEY ===\n");
                Console.Write("Recipient Account Number: ");
                string toAccount = Console.ReadLine() ?? string.Empty;
                Console.Write("Amount to send: $");
                if (!decimal.TryParse(Console.ReadLine(), out decimal amount) || amount <= 0)
                {
                    Console.WriteLine("\n❌ Invalid amount!");
                    return;
                }
                Console.Write("Description (optional): ");
                string description = Console.ReadLine() ?? string.Empty;

                var transferData = new { to_account = toAccount, amount, description };
                string json = JsonConvert.SerializeObject(transferData);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync($"{BASE_URL}/transfer/", content);
                string responseBody = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var result = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    Console.WriteLine($"\n✅ {result?.Message}");
                    Console.WriteLine($"💰 New Balance: {result?.NewBalance:C}");
                    
                    // Update current user balance
                    if (currentUser != null && result?.NewBalance != null)
                        currentUser.Balance = result.NewBalance;
                }
                else
                {
                    var error = JsonConvert.DeserializeObject<ApiResponse>(responseBody);
                    Console.WriteLine($"\n❌ Transfer failed: {error?.Error}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
            }
        }

        static async Task ViewProfile()
        {
            try
            {
                HttpResponseMessage response = await httpClient.GetAsync($"{BASE_URL}/profile/");
                string responseBody = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var profile = JsonConvert.DeserializeObject<User>(responseBody);
                    Console.WriteLine("\n👤 === USER PROFILE ===\n");
                    Console.WriteLine($"🆔 User ID: {profile?.Id}");
                    Console.WriteLine($"👤 Username: {profile?.Username}");
                    Console.WriteLine($"📧 Email: {profile?.Email}");
                    Console.WriteLine($"🏦 Account Number: {profile?.AccountNumber}");
                    Console.WriteLine($"💰 Balance: {profile?.Balance:C}");
                    Console.WriteLine($"📞 Phone: {profile?.Phone}");
                    Console.WriteLine($"📅 Member Since: {profile?.CreatedAt:MMMM dd, yyyy}");
                }
                else
                {
                    Console.WriteLine("\n❌ Failed to fetch profile!");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
            }
        }

        static async Task ViewTransactions()
        {
            try
            {
                HttpResponseMessage response = await httpClient.GetAsync($"{BASE_URL}/transactions/");
                string responseBody = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var transactions = JsonConvert.DeserializeObject<List<Transaction>>(responseBody);
                    Console.WriteLine("\n📜 === TRANSACTION HISTORY ===\n");
                    
                    if (transactions == null || !transactions.Any())
                    {
                        Console.WriteLine("No transactions found.");
                        return;
                    }
                    
                    Console.WriteLine("┌────────┬──────────────────────┬────────────┬──────────┐");
                    Console.WriteLine("│ Type   │ Date/Time            │ Amount     │ Details  │");
                    Console.WriteLine("├────────┼──────────────────────┼────────────┼──────────┤");
                    
                    foreach (var transaction in transactions.Take(20))
                    {
                        string type = transaction.TransactionType;
                        string amount = transaction.Amount.ToString("C");
                        string details = "";
                        
                        if (type == "TRANSFER")
                        {
                            if (transaction.FromUsername == currentUser?.Username)
                                details = $"To: {transaction.ToUsername}";
                            else
                                details = $"From: {transaction.FromUsername}";
                        }
                        else
                        {
                            details = transaction.Description ?? type;
                        }
                        
                        Console.WriteLine($"│ {type,-6} │ {transaction.Timestamp:yyyy-MM-dd HH:mm} │ {amount,-10} │ {details,-8} │");
                    }
                    
                    Console.WriteLine("└────────┴──────────────────────┴────────────┴──────────┘");
                }
                else
                {
                    Console.WriteLine("\n❌ Failed to fetch transactions!");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n❌ Error: {ex.Message}");
            }
        }

        static void PrintHeader()
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("╔══════════════════════════════════════════════╗");
            Console.WriteLine("║         🌉 BANKBRIDGE BANKING SYSTEM 🌉        ║");
            Console.WriteLine("║         Your Trusted Financial Partner         ║");
            Console.WriteLine("╚══════════════════════════════════════════════╝");
            Console.ResetColor();
        }

        static void PressEnter()
        {
            Console.Write("\n⏎ Press Enter to continue...");
            Console.ReadLine();
        }
    }
}