import {useEffect} from 'react';
import {useHistory, useLocation} from '@docusaurus/router';

export default function Home() {
  const history = useHistory();
  const location = useLocation();
  
  useEffect(() => {
    // Check if we're in Korean locale
    const isKorean = location.pathname.startsWith('/ko');
    
    // Redirect to appropriate introduction page
    if (isKorean) {
      history.replace('/ko/introduction');
    } else {
      history.replace('/introduction');
    }
  }, [history, location]);
  
  return null;
}
