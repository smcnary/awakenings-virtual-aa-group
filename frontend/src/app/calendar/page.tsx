export default function Calendar() {
  return (
    <div>
        {/* Hero Section */}
        <section className="bg-white rounded-lg shadow-lg p-8 mb-8 text-center">
          <h2 className="text-3xl font-bold text-slate-800 mb-4">Calendar</h2>
          <p className="text-lg text-gray-600">Upcoming events and special meetings</p>
        </section>

        {/* Content */}
        <div className="space-y-8">
          <section className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 mb-4 border-b-2 border-blue-500 pb-2">Regular Meeting Schedule</h3>
            <p className="text-gray-600 mb-6">Our group meets daily at 7:00 a.m. Central Time</p>
            
            <div className="grid gap-4">
              <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-blue-500">
                <h4 className="text-xl font-semibold text-slate-800 mb-2">Monday - Saturday</h4>
                <p className="text-gray-600 mb-1">Online with video option and phone access</p>
                <p className="text-gray-600 mb-1"><strong>Time:</strong> 7:00 a.m. Central Time</p>
                <p className="text-gray-600"><strong>Platform:</strong> FreeConferenceCall.com</p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-blue-500">
                <h4 className="text-xl font-semibold text-slate-800 mb-2">Sunday</h4>
                <p className="text-gray-600 mb-1">Phone and online only</p>
                <p className="text-gray-600 mb-1"><strong>Time:</strong> 7:00 a.m. Central Time</p>
                <p className="text-gray-600"><strong>Platform:</strong> FreeConferenceCall.com</p>
              </div>
            </div>
          </section>

          <section className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 mb-4 border-b-2 border-blue-500 pb-2">Special Events</h3>
            <p className="text-gray-600 mb-6">Upcoming special meetings and events:</p>
            
            <div className="grid gap-4">
              <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-red-500">
                <h4 className="text-xl font-semibold text-slate-800 mb-2">Group Anniversary</h4>
                <p className="text-gray-600 mb-1"><strong>Date:</strong> To be announced</p>
                <p className="text-gray-600 mb-1"><strong>Time:</strong> 7:00 a.m. Central Time</p>
                <p className="text-gray-600">Celebrate another year of recovery together</p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-red-500">
                <h4 className="text-xl font-semibold text-slate-800 mb-2">Speaker Meeting</h4>
                <p className="text-gray-600 mb-1"><strong>Date:</strong> First Friday of each month</p>
                <p className="text-gray-600 mb-1"><strong>Time:</strong> 7:00 a.m. Central Time</p>
                <p className="text-gray-600">Special speaker shares their experience, strength, and hope</p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-red-500">
                <h4 className="text-xl font-semibold text-slate-800 mb-2">Step Study Meeting</h4>
                <p className="text-gray-600 mb-1"><strong>Date:</strong> Third Saturday of each month</p>
                <p className="text-gray-600 mb-1"><strong>Time:</strong> 7:00 a.m. Central Time</p>
                <p className="text-gray-600">In-depth study of the Twelve Steps</p>
              </div>
            </div>
          </section>

          <section className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 mb-4 border-b-2 border-blue-500 pb-2">Meeting Access Information</h3>
            <p className="text-gray-600 mb-6">Join our meetings using the following information:</p>
            
            <div className="grid gap-4">
              <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-green-500">
                <h4 className="text-xl font-semibold text-slate-800 mb-2">Online Meeting</h4>
                <p className="text-gray-600 mb-1">
                  <strong>Link:</strong>{" "}
                  <a 
                    href="https://join.freeconferencecall.com/timhwalton" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    https://join.freeconferencecall.com/timhwalton
                  </a>
                </p>
                <p className="text-gray-600"><strong>Meeting ID:</strong> timhwalton</p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg border-l-4 border-green-500">
                <h4 className="text-xl font-semibold text-slate-800 mb-2">Phone Access</h4>
                <p className="text-gray-600 mb-1">
                  <strong>US Dial-in:</strong>{" "}
                  <a href="tel:+19517999267" className="text-blue-600 hover:text-blue-800">
                    (951) 799-9267
                  </a>
                </p>
                <p className="text-gray-600">
                  <strong>International:</strong>{" "}
                  <a 
                    href="https://fccdl.in/i/timhwalton" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    https://fccdl.in/i/timhwalton
                  </a>
                </p>
              </div>
            </div>
          </section>

          <section className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-slate-800 mb-4 border-b-2 border-blue-500 pb-2">Time Zone Information</h3>
            <p className="text-gray-600 mb-6">Our meetings are held at 7:00 a.m. Central Time. Here's what that means for other time zones:</p>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 mb-2">Eastern Time</h4>
                <p className="text-gray-600 font-semibold">8:00 a.m.</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 mb-2">Mountain Time</h4>
                <p className="text-gray-600 font-semibold">6:00 a.m.</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 mb-2">Pacific Time</h4>
                <p className="text-gray-600 font-semibold">5:00 a.m.</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 mb-2">Alaska Time</h4>
                <p className="text-gray-600 font-semibold">4:00 a.m.</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <h4 className="text-lg font-semibold text-slate-800 mb-2">Hawaii Time</h4>
                <p className="text-gray-600 font-semibold">2:00 a.m.</p>
              </div>
            </div>
            
            <p className="text-gray-600 italic mt-6">Note: Times adjust for Daylight Saving Time changes.</p>
          </section>
        </div>
    </div>
  );
}
