export default function SeventhTradition() {
  return (
    <div>
        {/* Hero Section */}
        <section className="bg-white rounded-lg shadow-lg p-8 mb-8 text-center">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">7th Tradition</h2>
          <p className="text-lg text-gray-600 italic">"Every A.A. group ought to be fully self-supporting, declining outside contributions."</p>
        </section>

        {/* Content */}
        <div className="space-y-8">
          <section className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 mb-4 border-b-2 border-blue-500 pb-2">Self-Supporting Through Our Own Contributions</h3>
            <p className="text-gray-600 mb-6">AA Group name to be determined is fully self-supporting through the voluntary contributions of our members. We follow the 7th Tradition of Alcoholics Anonymous, which states that every A.A. group should be fully self-supporting and decline outside contributions.</p>
            
            <div className="bg-gray-50 p-6 rounded-lg">
              <h4 className="text-xl font-semibold text-slate-800 mb-4">How We Support Our Group</h4>
              <ul className="space-y-2 text-gray-600">
                <li>• Voluntary contributions from members</li>
                <li>• No dues or fees required</li>
                <li>• Contributions support meeting expenses, literature, and service work</li>
                <li>• Any excess funds are passed along to support the broader A.A. service structure</li>
              </ul>
            </div>
          </section>

          <section className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 mb-4 border-b-2 border-blue-500 pb-2">Ways to Contribute</h3>
            <p className="text-gray-600 mb-6">There are several ways you can support our group:</p>
            
            <div className="grid gap-6">
              <div className="bg-gray-50 p-6 rounded-lg">
                <h4 className="text-xl font-semibold text-slate-800 mb-4">Digital Contributions</h4>
                <p className="text-gray-600 mb-2">We accept contributions through:</p>
                <ul className="space-y-1 text-gray-600 mb-4">
                  <li>• Venmo</li>
                  <li>• PayPal</li>
                </ul>
                <p className="text-gray-600 italic">Contact information for digital contributions will be provided at meetings.</p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg">
                <h4 className="text-xl font-semibold text-slate-800 mb-4">Service Contributions</h4>
                <p className="text-gray-600 mb-2">Your time and service are equally valuable:</p>
                <ul className="space-y-1 text-gray-600">
                  <li>• Volunteering for group service positions</li>
                  <li>• Helping with meeting setup and cleanup</li>
                  <li>• Sharing your experience, strength, and hope</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 mb-4 border-b-2 border-blue-500 pb-2">Financial Transparency</h3>
            <p className="text-gray-600 mb-6">Our group maintains transparency in how contributions are used. Regular reports are provided at group business meetings, and all members are welcome to participate in financial decisions.</p>
            
            <div className="bg-gray-50 p-6 rounded-lg">
              <h4 className="text-xl font-semibold text-slate-800 mb-4">Typical Group Expenses Include:</h4>
              <ul className="space-y-2 text-gray-600">
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
