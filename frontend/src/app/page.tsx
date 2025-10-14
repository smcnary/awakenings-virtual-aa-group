export default function Home() {
  return (
    <div>
        {/* Hero Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 text-center transition-colors">
          <h2 className="text-3xl font-bold text-slate-800 dark:text-white mb-4">Awakening Group Information</h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-2">AA Group name to be determined is an Online AA group of Alcoholics Anonymous World Services</p>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-2">We meet Monday through Sunday at 7:00 a.m. Central Time</p>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-2">Our primary purpose is to stay sober and to help others recover from alcoholism</p>
          <p className="text-lg text-gray-600 dark:text-gray-300">We welcome anyone who wishes to join us on a path of recovery</p>
        </section>

        {/* Meetings Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 transition-colors">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6 text-center border-b-2 border-blue-500 pb-2">REMOTE MEETINGS</h2>
          <div className="text-center">
            <p className="text-xl font-semibold mb-8 text-red-600 dark:text-red-400">Every day at 7:00 a.m. Central Time</p>
            
            <div className="bg-gray-50 dark:bg-gray-700 p-6 mb-6 rounded-lg border-l-4 border-blue-500 transition-colors">
              <h3 className="text-xl font-semibold text-slate-800 dark:text-white mb-4">Online with Video Option</h3>
              <p className="mb-2 text-gray-600 dark:text-gray-300">
                <strong>Meeting Link:</strong>{" "}
                <a 
                  href="https://join.freeconferencecall.com/timhwalton" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  https://join.freeconferencecall.com/timhwalton
                </a>
              </p>
              <p className="text-gray-600 dark:text-gray-300">
                <strong>Online Meeting ID:</strong> timhwalton
              </p>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 p-6 mb-6 rounded-lg border-l-4 border-blue-500 transition-colors">
              <h3 className="text-xl font-semibold text-slate-800 dark:text-white mb-4">Phone Only</h3>
              <p className="mb-2 text-gray-600 dark:text-gray-300">
                <strong>Dial-in number (US):</strong>{" "}
                <a href="tel:+19517999267" className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                  (951) 799-9267
                </a>
              </p>
              <p className="text-gray-600 dark:text-gray-300">
                <strong>International dial-in numbers:</strong>{" "}
                <a 
                  href="https://fccdl.in/i/timhwalton" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  https://fccdl.in/i/timhwalton
                </a>
              </p>
            </div>
          </div>
        </section>

        {/* Resources Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 transition-colors">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6 text-center border-b-2 border-blue-500 pb-2">RESOURCES</h2>
          <div className="flex justify-center gap-8 flex-wrap">
            <a 
              href="https://www.aa.org/find-aa" 
              target="_blank" 
              rel="noopener noreferrer"
              className="bg-blue-600 dark:bg-blue-700 text-white px-8 py-4 rounded-lg font-medium hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
            >
              Meeting Finder
            </a>
            <a 
              href="https://www.aa.org/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="bg-blue-600 dark:bg-blue-700 text-white px-8 py-4 rounded-lg font-medium hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
            >
              A.A. World Services
            </a>
          </div>
        </section>

        {/* Service Structure Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 transition-colors">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6 text-center border-b-2 border-blue-500 pb-2">A.A. SERVICE STRUCTURE</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <a href="#" className="bg-gray-100 dark:bg-gray-700 text-slate-800 dark:text-white p-4 rounded-lg text-center font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
              Northeast Central Service
            </a>
            <a href="#" className="bg-gray-100 dark:bg-gray-700 text-slate-800 dark:text-white p-4 rounded-lg text-center font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
              District 30
            </a>
            <a href="#" className="bg-gray-100 dark:bg-gray-700 text-slate-800 dark:text-white p-4 rounded-lg text-center font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
              Area 57
            </a>
            <a 
              href="https://www.aa.org/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="bg-gray-100 dark:bg-gray-700 text-slate-800 dark:text-white p-4 rounded-lg text-center font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors md:col-span-2 lg:col-span-1"
            >
              General Service Office NYC
            </a>
          </div>
        </section>

        {/* Contact Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mb-8 transition-colors">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-6 text-center border-b-2 border-blue-500 pb-2">CONTACT</h2>
          <div className="space-y-4 text-gray-600 dark:text-gray-300 leading-relaxed">
            <p>We have a private Facebook Group you may request to join.</p>
            <p>
              You may contact us through our private Facebook Group. Please request to join and we&apos;ll respond as soon as possible.
            </p>
            <p>If your need is more immediate, please call your sponsor or another group member, or find a meeting, or reach out to Northeast Central Service.</p>
            <p>We welcome you to join us at our regular daily meetings, Mon-Sun at 7:00 am.</p>
          </div>
        </section>
    </div>
  );
}