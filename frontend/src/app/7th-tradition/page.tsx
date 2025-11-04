export default function SeventhTradition() {
  return (
    <div>
        {/* Hero Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 text-center transition-colors">
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white mb-4">7th Tradition</h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 italic">"Every A.A. group ought to be fully self-supporting, declining outside contributions."</p>
        </section>

        {/* Content */}
        <div className="space-y-8">
          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 border-b-2 border-blue-500 pb-2">Self-Supporting Through Our Own Contributions</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">AA Group name to be determined is fully self-supporting through the voluntary contributions of our members. We follow the 7th Tradition of Alcoholics Anonymous, which states that every A.A. group should be fully self-supporting and decline outside contributions.</p>
            
            <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg">
              <h4 className="text-xl font-semibold text-slate-800 dark:text-white mb-4">How We Support Our Group</h4>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400">
                <li>• Voluntary contributions from members</li>
                <li>• No dues or fees required</li>
                <li>• Contributions support meeting expenses, literature, and service work</li>
                <li>• Any excess funds are passed along to support the broader A.A. service structure</li>
              </ul>
            </div>
          </section>

          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 border-b-2 border-blue-500 pb-2">Ways to Contribute</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">There are several ways you can support our group:</p>
            
            <div className="grid gap-6">
              <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg">
                <h4 className="text-xl font-semibold text-slate-800 dark:text-white mb-4">Digital Contributions</h4>
                <p className="text-gray-600 dark:text-gray-400 mb-4">We accept contributions through:</p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-4">
                  <a 
                    href="https://venmo.com/your-username"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-[#3D95CE] hover:bg-[#2d7aa8] text-white px-8 py-4 rounded-lg font-semibold text-center min-w-[140px] transition-colors"
                  >
                    Venmo
                  </a>
                  <a 
                    href="https://www.paypal.com/donate/your-donation-link"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-[#0070BA] hover:bg-[#005a94] text-white px-8 py-4 rounded-lg font-semibold text-center min-w-[140px] transition-colors"
                  >
                    PayPal
                  </a>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-500 italic text-center">
                  Replace URLs with your actual Venmo username and PayPal donation link
                </p>
              </div>
              
              <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg">
                <h4 className="text-xl font-semibold text-slate-800 dark:text-white mb-4">Service Contributions</h4>
                <p className="text-gray-600 dark:text-gray-400 mb-2">Your time and service are equally valuable:</p>
                <ul className="space-y-1 text-gray-600 dark:text-gray-400">
                  <li>• Volunteering for group service positions</li>
                  <li>• Helping with meeting setup and cleanup</li>
                  <li>• Sharing your experience, strength, and hope</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 border-b-2 border-blue-500 pb-2">Financial Transparency</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Our group maintains transparency in how contributions are used. Regular reports are provided at group business meetings, and all members are welcome to participate in financial decisions.</p>
            
            <div className="bg-gray-50 dark:bg-gray-700 p-6 rounded-lg">
              <h4 className="text-xl font-semibold text-slate-800 dark:text-white mb-4">Typical Group Expenses Include:</h4>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400">
                <li>• Meeting platform subscriptions</li>
                <li>• A.A. literature and materials</li>
                <li>• Service work contributions to District, Area, and GSO</li>
                <li>• Group anniversary celebrations</li>
              </ul>
            </div>
          </section>
        </div>
    </div>
  );
}
